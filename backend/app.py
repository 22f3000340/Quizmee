from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, timedelta
import os
from functools import wraps
import utils

# Initialize Flask app
app = Flask(__name__)
# Use an absolute path for the database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'quizmaster.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize CORS with a configuration that works for all routes
CORS(app, 
     resources={r"/api/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}},
     supports_credentials=True)

# Add CORS headers to all responses, including error responses
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    # If the request has an Origin header and it's one of our allowed origins
    if origin in ["http://localhost:8080", "http://127.0.0.1:8080"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response.status_code = 200
    return response

# Special handling for OPTIONS requests (preflight)
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return jsonify({}), 200

jwt = JWTManager(app)
db.init_app(app)

# Define a helper function to check admin privileges
def check_admin_access():
    # Get additional claims from JWT token
    claims = get_jwt()
    # Check if user has admin privileges
    if not claims.get('is_admin'):
        return jsonify({"msg": "Admin privileges required"}), 403
    return None

# Authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        # Use username as the identity (subject) and include other data as additional claims
        access_token = create_access_token(
            identity=username,
            additional_claims={
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        )
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }), 200
    else:
        return jsonify({"msg": "Invalid username or password"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    # Check if username or email already exists
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "Email already exists"}), 400
    
    # Generate a professional-looking ID
    new_id = utils.get_next_id(db.session, User, 'user')
    
    # Create new user
    user = User(
        id=new_id,
        username=data.get('username'),
        full_name=data.get('full_name'),
        email=data.get('email'),
        qualification=data.get('qualification'),
        date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
        is_admin=False
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    # Ensure SQLite sequence is updated
    utils.ensure_id_sequence(db.session, User, 'user')
    
    return jsonify({"msg": "User registered successfully"}), 201

# User routes
@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    # Get the identity (username) and additional claims
    current_user_identity = get_jwt_identity()
    current_user_claims = get_jwt()
    
    # Check if user has admin privileges
    if not current_user_claims.get('is_admin'):
        return jsonify({"msg": "Admin privileges required"}), 403
    
    users = User.query.all()  # Get all users including admins
    
    return jsonify({
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'qualification': user.qualification,
                'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
                'is_admin': user.is_admin
            }
            for user in users
        ]
    }), 200

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    # Get the identity (username) from the JWT
    current_username = get_jwt_identity()
    
    # Find the user in the database
    user = User.query.filter_by(username=current_username).first()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # Return user profile data
    return jsonify({
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'qualification': user.qualification,
        'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
        'is_admin': user.is_admin
    }), 200

@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    # Get the identity (username) from the JWT
    current_username = get_jwt_identity()
    
    # Find the user in the database
    user = User.query.filter_by(username=current_username).first()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    # Check if email is being changed and if it already exists
    if data.get('email') and data.get('email') != user.email:
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({"msg": "Email already in use"}), 400
    
    # Update user fields
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.qualification = data.get('qualification', user.qualification)
    
    # Handle date_of_birth
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Update password if provided
    if data.get('password'):
        user.set_password(data.get('password'))
    
    db.session.commit()
    
    # Return updated profile
    return jsonify({
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'qualification': user.qualification,
        'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
        'is_admin': user.is_admin
    }), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # Get the identity and claims from JWT
    current_user_identity = get_jwt_identity()
    current_user_claims = get_jwt()
    
    # Check if user has admin privileges
    if not current_user_claims.get('is_admin'):
        return jsonify({"msg": "Admin privileges required"}), 403
    
    # Find the user to delete
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # Prevent deleting yourself
    current_user = User.query.filter_by(username=current_user_identity).first()
    if user.id == current_user.id:
        return jsonify({"msg": "Cannot delete your own account"}), 400
    
    # Delete related records (scores, etc.) to prevent foreign key constraint errors
    Score.query.filter_by(user_id=user.id).delete()
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"msg": "User deleted successfully"}), 200

# Subject routes
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    
    return jsonify({
        'subjects': [
            {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description
            }
            for subject in subjects
        ]
    }), 200

@app.route('/api/subjects/<int:subject_id>', methods=['GET'])
def get_subject_by_id(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }), 200

@app.route('/api/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    # Generate a professional-looking ID
    new_id = utils.get_next_id(db.session, Subject, 'subject')
    
    # Create new subject
    subject = Subject(
        id=new_id,
        name=data.get('name'),
        description=data.get('description')
    )
    
    try:
        db.session.add(subject)
        db.session.commit()
        
        # Ensure SQLite sequence is updated
        utils.ensure_id_sequence(db.session, Subject, 'subject')
        
        return jsonify({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creating subject: {str(e)}"}), 500

@app.route('/api/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
def update_subject(subject_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
        
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    subject = Subject.query.get_or_404(subject_id)
    data = request.json
    
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    
    db.session.commit()
    
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }), 200

@app.route('/api/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    # Get subject by ID
    subject = Subject.query.get_or_404(subject_id)
    
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({"msg": "Subject deleted successfully"}), 200

# Chapter routes
@app.route('/api/subjects/<int:subject_id>/chapters', methods=['GET'])
def get_chapters(subject_id):
    Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    return jsonify({
        'chapters': [
            {
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'subject_id': chapter.subject_id
            }
            for chapter in chapters
        ]
    }), 200

@app.route('/api/subjects/<int:subject_id>/chapters', methods=['POST'])
@jwt_required()
def create_chapter(subject_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    # Get subject
    subject = Subject.query.get_or_404(subject_id)
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    # Generate a professional-looking ID
    new_id = utils.get_next_id(db.session, Chapter, 'chapter')
    
    chapter = Chapter(
        id=new_id,
        name=data.get('name'),
        description=data.get('description'),
        subject_id=subject_id
    )
    
    try:
        db.session.add(chapter)
        db.session.commit()
        
        # Ensure SQLite sequence is updated
        utils.ensure_id_sequence(db.session, Chapter, 'chapter')
        
        return jsonify({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'subject_id': chapter.subject_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creating chapter: {str(e)}"}), 500

@app.route('/api/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
def update_chapter(chapter_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.json
    
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)
    
    db.session.commit()
    
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id
    }), 200

@app.route('/api/chapters/<int:chapter_id>', methods=['GET'])
def get_chapter_by_id(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id
    }), 200

@app.route('/api/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
def delete_chapter(chapter_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    current_user = get_jwt_identity()
    
    if not current_user.get('is_admin'):
        return jsonify({"msg": "Admin privileges required"}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    db.session.delete(chapter)
    db.session.commit()
    
    return jsonify({"msg": "Chapter deleted successfully"}), 200

# Quiz routes
@app.route('/api/chapters/<int:chapter_id>/quizzes', methods=['GET'])
def get_quizzes(chapter_id):
    Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    result = []
    for quiz in quizzes:
        # Get the number of questions for this quiz
        question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        
        result.append({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'chapter_id': quiz.chapter_id,
            'duration': quiz.duration,
            'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S'),
            'remarks': quiz.remarks,
            'question_count': question_count
        })
    
    return jsonify({
        'quizzes': result
    }), 200

@app.route('/api/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@jwt_required()
def create_quiz(chapter_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    # Get chapter 
    Chapter.query.get_or_404(chapter_id)
    data = request.json
    
    try:
        # Generate a professional-looking ID
        new_id = utils.get_next_id(db.session, Quiz, 'quiz')
        
        # Create a new quiz with the provided data
        quiz = Quiz(
            id=new_id,
            title=data.get('title'),
            description=data.get('description', ''),
            duration=int(data.get('duration', 30)),
            chapter_id=chapter_id,
            date_of_quiz=datetime.utcnow(),  # Default to current time
            remarks=''  # Empty remarks by default
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        # Ensure SQLite sequence is updated
        utils.ensure_id_sequence(db.session, Quiz, 'quiz')
        
        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'duration': quiz.duration,
            'chapter_id': quiz.chapter_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creating quiz: {str(e)}"}), 500

@app.route('/api/quizzes/<int:quiz_id>', methods=['PUT'])
@jwt_required()
def update_quiz(quiz_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
        
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.json
    
    quiz.title = data.get('title', quiz.title)
    quiz.description = data.get('description', quiz.description)
    quiz.duration = data.get('duration', quiz.duration)
    
    db.session.commit()
    
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'duration': quiz.duration,
        'chapter_id': quiz.chapter_id
    }), 200

@app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
def get_quiz_by_id(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get the number of questions for this quiz
    question_count = Question.query.filter_by(quiz_id=quiz_id).count()
    
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'duration': quiz.duration,
        'chapter_id': quiz.chapter_id,
        'question_count': question_count
    }), 200

@app.route('/api/quizzes/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
def delete_quiz(quiz_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    current_user = get_jwt_identity()
    
    if not current_user.get('is_admin'):
        return jsonify({"msg": "Admin privileges required"}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    db.session.delete(quiz)
    db.session.commit()
    
    return jsonify({"msg": "Quiz deleted successfully"}), 200

# Question routes
@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
def get_questions(quiz_id):
    # Verify quiz exists
    Quiz.query.get_or_404(quiz_id)
    
    # Get questions for this quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Get JWT claims to check if user is admin
    current_user_claims = get_jwt()
    is_admin = current_user_claims.get('is_admin', False)
    
    # Format response based on user role
    result = []
    for question in questions:
        question_data = {
            'id': question.id,
            'quiz_id': question.quiz_id,
            'question_text': question.question_text,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4
        }
        
        # Only include correct answer for admins
        if is_admin:
            question_data['correct_option'] = question.correct_option
            
        result.append(question_data)
    
    return jsonify({'questions': result}), 200

@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
def create_question(quiz_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    Quiz.query.get_or_404(quiz_id)
    data = request.json
    
    # Generate a professional-looking ID
    new_id = utils.get_next_id(db.session, Question, 'question')
    
    question = Question(
        id=new_id,
        quiz_id=quiz_id,
        question_text=data.get('question_text'),
        option1=data.get('option1'),
        option2=data.get('option2'),
        option3=data.get('option3'),
        option4=data.get('option4'),
        correct_option=data.get('correct_option')
    )
    
    db.session.add(question)
    db.session.commit()
    
    # Ensure SQLite sequence is updated
    utils.ensure_id_sequence(db.session, Question, 'question')
    
    return jsonify({
        'id': question.id,
        'quiz_id': question.quiz_id,
        'question_text': question.question_text,
        'option1': question.option1,
        'option2': question.option2,
        'option3': question.option3,
        'option4': question.option4,
        'correct_option': question.correct_option
    }), 201

@app.route('/api/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    current_user = get_jwt_identity()
    
    if not current_user.get('is_admin'):
        return jsonify({"msg": "Admin privileges required"}), 403
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    question = Question.query.get_or_404(question_id)
    data = request.json
    
    question.question_text = data.get('question_text', question.question_text)
    question.option1 = data.get('option1', question.option1)
    question.option2 = data.get('option2', question.option2)
    question.option3 = data.get('option3', question.option3)
    question.option4 = data.get('option4', question.option4)
    question.correct_option = data.get('correct_option', question.correct_option)
    
    db.session.commit()
    
    return jsonify({
        'id': question.id,
        'quiz_id': question.quiz_id,
        'question_text': question.question_text,
        'option1': question.option1,
        'option2': question.option2,
        'option3': question.option3,
        'option4': question.option4,
        'correct_option': question.correct_option
    }), 200

@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    question = Question.query.get_or_404(question_id)
    
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({"msg": "Question deleted successfully"}), 200

# Quiz attempt routes
@app.route('/api/quizzes/<int:quiz_id>/attempt', methods=['POST'])
@jwt_required()
def submit_quiz_attempt(quiz_id):
    try:
        current_username = get_jwt_identity()
        # Get additional claims to access user info
        claims = get_jwt()
        user_id = claims.get('id')
        
        # If user ID is not in claims, look it up by username
        if not user_id:
            user = User.query.filter_by(username=current_username).first()
            if not user:
                return jsonify({"msg": "User not found"}), 404
            user_id = user.id
        
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        
        # Check if quiz exists
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({"msg": "Quiz not found"}), 404
            
        data = request.json
        
        # Get the answers submitted by the user
        submitted_answers = data.get('answers', {})
        print(f"Received answers: {submitted_answers}")
        
        # Calculate score
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # Check if there are any questions for this quiz
        if not questions:
            return jsonify({"msg": "No questions found for this quiz"}), 400
            
        correct_answers = 0
        question_results = []
        
        for question in questions:
            # Convert question ID to string for comparison with JSON keys
            question_id_str = str(question.id)
            
            # Check if the user answered this question and if it's correct
            is_correct = False
            user_answer = None
            
            if question_id_str in submitted_answers:
                user_answer = submitted_answers[question_id_str]
                # Ensure user_answer and correct_option are comparable
                try:
                    # Convert both to integers for reliable comparison
                    user_answer_int = int(user_answer) if user_answer is not None else None
                    correct_option_int = int(question.correct_option) if question.correct_option is not None else None
                    
                    # Debug output
                    print(f"Question {question.id}: User answer = {user_answer_int} ({type(user_answer_int)}), Correct = {correct_option_int} ({type(correct_option_int)})")
                    
                    is_correct = user_answer_int == correct_option_int
                    
                    if is_correct:
                        correct_answers += 1
                        print(f"✓ Correct answer for question {question.id}")
                    else:
                        print(f"✗ Wrong answer for question {question.id}")
                        
                except (ValueError, TypeError) as e:
                    print(f"Error comparing answers for question {question.id}: {str(e)}")
                    is_correct = False
            
            # Store details about each question for debugging
            question_results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_option,
                'is_correct': is_correct
            })
        
        total_questions = len(questions)
        score_value = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        print(f"Score calculation: {correct_answers}/{total_questions} = {score_value}%")
        print(f"Question results: {question_results}")
        
        # Create score record
        try:
            # Generate a professional-looking ID
            print(f"Generating score ID for user {user_id}, quiz {quiz_id}")
            new_id = utils.get_next_id(db.session, Score, 'score')
            print(f"Generated score ID: {new_id}")
            
            score = Score(
                id=new_id,
                user_id=user_id,
                quiz_id=quiz_id,
                score=score_value,
                total_questions=total_questions,
                correct_answers=correct_answers,
                time_taken=data.get('time_taken', 0)
            )
            
            print(f"Adding score to session: {score.id}, user: {score.user_id}, quiz: {score.quiz_id}")
            db.session.add(score)
            db.session.commit()
            print(f"Score saved successfully with ID: {score.id}")
            
            # Ensure SQLite sequence is updated
            utils.ensure_id_sequence(db.session, Score, 'score')
            print(f"SQLite sequence updated for score table")
            
            return jsonify({
                'id': score.id,
                'quiz_id': score.quiz_id,
                'score': score.score,
                'total_questions': score.total_questions,
                'correct_answers': score.correct_answers,
                'time_taken': score.time_taken,
                'timestamp': score.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'question_results': question_results
            }), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error saving score: {str(e)}")
            return jsonify({"msg": f"Error saving score: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Error processing quiz attempt: {str(e)}")
        return jsonify({"msg": f"Error processing quiz attempt: {str(e)}"}), 500

# User scores
@app.route('/api/users/scores', methods=['GET'])
@jwt_required()
def get_user_scores():
    current_username = get_jwt_identity()
    # Get additional claims to access user info
    claims = get_jwt()
    user_id = claims.get('id')
    
    # If user ID is not in claims, look it up by username
    if not user_id:
        user = User.query.filter_by(username=current_username).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
        user_id = user.id
    
    # Get all user scores
    scores = Score.query.filter_by(user_id=user_id).all()
    
    # Build detailed score list
    score_details = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
        subject = Subject.query.get(chapter.subject_id) if chapter else None
        
        score_details.append({
            'id': score.id,
            'quiz_id': score.quiz_id,
            'quiz_title': quiz.title if quiz else "Unknown Quiz",
            'chapter_name': chapter.name if chapter else "Unknown Chapter",
            'subject_name': subject.name if subject else "Unknown Subject",
            'score': score.score,
            'total_questions': score.total_questions,
            'correct_answers': score.correct_answers,
            'time_taken': score.time_taken,
            'timestamp': score.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Get count of all subjects
    subjects_count = Subject.query.count()
    
    # Calculate average score
    average_score = 0
    if scores:
        average_score = round(sum(score.score for score in scores) / len(scores), 1)
    
    # Get recent scores (last 5)
    recent_scores = []
    for score_detail in sorted(score_details, key=lambda x: x['timestamp'], reverse=True)[:5]:
        recent_scores.append({
            'id': score_detail['id'],
            'quizName': score_detail['quiz_title'],
            'date': score_detail['timestamp'],
            'score': round(score_detail['score'], 1)
        })
    
    # Calculate subject progress
    subject_progress = []
    subjects = Subject.query.all()
    
    for subject in subjects:
        # Get all chapters for this subject
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        chapter_ids = [chapter.id for chapter in chapters]
        
        # Get all quizzes for these chapters
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
        quiz_ids = [quiz.id for quiz in quizzes]
        
        # Get all scores for these quizzes by this user
        user_scores = Score.query.filter(Score.quiz_id.in_(quiz_ids), Score.user_id == user_id).all()
        
        # Calculate progress percentage based on quizzes attempted vs total quizzes
        progress = 0
        if quizzes:
            completed_quizzes = len(set(score.quiz_id for score in user_scores))
            progress = round((completed_quizzes / len(quizzes)) * 100)
        
        subject_progress.append({
            'id': subject.id,
            'name': subject.name,
            'progress': progress
        })
    
    return jsonify({
        'scores': score_details,
        'subjects_count': subjects_count,
        'attempts_count': len(scores),
        'average_score': average_score,
        'recent_scores': recent_scores,
        'subject_progress': subject_progress
    }), 200

# Statistics routes for admin
@app.route('/api/admin/statistics', methods=['GET'])
@jwt_required()
def get_admin_statistics():
    # Check admin privileges
    admin_check = check_admin_access()
    if admin_check:
        return admin_check
    
    # Count total users, subjects, chapters, quizzes
    user_count = User.query.filter_by(is_admin=False).count()
    subject_count = Subject.query.count()
    chapter_count = Chapter.query.count()
    quiz_count = Quiz.query.count()
    question_count = Question.query.count()
    attempt_count = Score.query.count()
    
    # Debug logging for quiz counts
    print(f"Total quiz count: {quiz_count}")
    print(f"Total chapter count: {chapter_count}")
    
    # Get all quizzes and check their chapter associations
    all_quizzes = Quiz.query.all()
    quizzes_without_chapters = [q for q in all_quizzes if not q.chapter_id]
    print(f"Quizzes without chapters: {len(quizzes_without_chapters)}")
    if quizzes_without_chapters:
        print("Quiz IDs without chapters:", [q.id for q in quizzes_without_chapters])
    
    # Get average scores per subject
    subjects = Subject.query.all()
    subject_scores = []
    
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        chapter_ids = [chapter.id for chapter in chapters]
        
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
        quiz_ids = [quiz.id for quiz in quizzes]
        
        scores = Score.query.filter(Score.quiz_id.in_(quiz_ids)).all()
        avg_score = sum(score.score for score in scores) / len(scores) if scores else 0
        
        subject_scores.append({
            'id': subject.id,
            'name': subject.name,
            'avgScore': round(avg_score, 1),
            'attempts': len(scores)
        })
    
    # Generate recent activity data
    recent_activity = []
    # Get recent quiz attempts
    recent_scores = Score.query.order_by(Score.timestamp.desc()).limit(5).all()
    for score in recent_scores:
        quiz = Quiz.query.get(score.quiz_id)
        user = User.query.get(score.user_id)
        if quiz and user:
            recent_activity.append({
                'id': score.id,
                'user': user.username,
                'action': 'completed a quiz',
                'details': f'Scored {score.score}% on {quiz.title}',
                'type': 'Quiz Completion',
                'timestamp': score.timestamp.isoformat()
            })
    
    # Get recent content updates (quizzes)
    recent_quizzes = Quiz.query.order_by(Quiz.id.desc()).limit(3).all()
    for quiz in recent_quizzes:
        recent_activity.append({
            'id': quiz.id,
            'user': 'System',  # Using 'System' since created_by doesn't exist
            'action': 'created a quiz',
            'details': f'Added {quiz.title}',
            'type': 'Content Update',
            'timestamp': quiz.created_at.isoformat() if hasattr(quiz, 'created_at') else datetime.utcnow().isoformat()
        })
    
    # Get recent user registrations
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(3).all()
    for user in recent_users:
        recent_activity.append({
            'id': user.id,
            'user': user.username,
            'action': 'registered',
            'details': 'New user registration',
            'type': 'Registration',
            'timestamp': user.created_at.isoformat()
        })
    
    # Sort recent activity by timestamp
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Calculate user growth
    current_date = datetime.utcnow()
    last_month_start = current_date.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_start.replace(day=1)
    current_month_start = current_date.replace(day=1)
    
    # Get user counts for different periods
    total_users_current = User.query.filter_by(is_admin=False).count()
    total_users_last_month_end = User.query.filter(
        User.is_admin == False,
        User.created_at <= last_month_start
    ).count()
    
    current_month_users = User.query.filter(
        User.is_admin == False,
        User.created_at >= current_month_start
    ).count()
    
    last_month_users = User.query.filter(
        User.is_admin == False,
        User.created_at >= last_month_start,
        User.created_at < current_month_start
    ).count()
    
    # Calculate growth percentage
    if total_users_last_month_end > 0:
        growth_percentage = ((total_users_current - total_users_last_month_end) / total_users_last_month_end) * 100
    else:
        growth_percentage = 100 if total_users_current > 0 else 0
    
    # Calculate projected growth
    days_in_current_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    days_elapsed = current_date.day
    days_remaining = days_in_current_month.day - days_elapsed
    
    if days_elapsed > 0:
        daily_new_users = current_month_users / days_elapsed
        projected_new_users = int(daily_new_users * days_remaining)
        projected_total_users = total_users_current + projected_new_users
    else:
        projected_new_users = 0
        projected_total_users = total_users_current
    
    # Package the data for the frontend
    user_growth = {
        'percentage': growth_percentage,
        'last_month_new': last_month_users,
        'current_month_new': current_month_users, 
        'last_month_total': total_users_last_month_end,
        'current_month_total': total_users_current,
        'projected_new': projected_new_users,
        'projected_total': projected_total_users
    }
    
    # Generate quiz distribution data
    quiz_distribution = []
    total_distributed_quizzes = 0
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        chapter_ids = [chapter.id for chapter in chapters]
        subject_quiz_count = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).count()
        total_distributed_quizzes += subject_quiz_count
        
        if subject_quiz_count > 0:
            quiz_distribution.append({
                'subject': subject.name,
                'count': subject_quiz_count
            })
    
    # Debug logging for quiz distribution
    print(f"Total distributed quizzes: {total_distributed_quizzes}")
    print(f"Quiz distribution: {quiz_distribution}")
    
    return jsonify({
        'counts': {
            'users': user_count,
            'subjects': subject_count,
            'quizzes': quiz_count,
            'attempts': attempt_count
        },
        'count_metadata': {
            'users': {
                'label': 'Registered Users',
                'total': user_count
            },
            'subjects': {
                'label': 'Available Subjects',
                'total': subject_count
            },
            'quizzes': {
                'label': 'Total Quizzes',
                'total': quiz_count,
                'description': 'All quizzes in the system'
            },
            'attempts': {
                'label': 'Quiz Attempts',
                'total': attempt_count
            }
        },
        'subject_scores': subject_scores,
        'recent_activity': recent_activity,
        'user_growth': user_growth,
        'quiz_distribution': quiz_distribution
    }), 200

# Test route to check database operations
@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        # Test read operation
        user_count = User.query.count()
        
        # Test write operation
        test_timestamp = datetime.utcnow()
        
        # Return success
        return jsonify({
            'status': 'success',
            'message': 'Database operations are working correctly',
            'user_count': user_count,
            'timestamp': test_timestamp.isoformat()
        }), 200
    except Exception as e:
        # Return error details
        return jsonify({
            'status': 'error',
            'message': 'Database operation failed',
            'error': str(e)
        }), 500

# Helper function to check if in app context and create it if needed
def ensure_app_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if app.app_context().get_current_object() is None:
            with app.app_context():
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper

if __name__ == '__main__':
    # Create the database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Initialize database within app context
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
            
            # Check if admin user exists, if not create one
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                admin = User(
                    username='admin',
                    full_name='Administrator',
                    email='admin@quizmaster.com',
                    is_admin=True
                )
                admin.set_password('admin123')  # Change this in production
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully!")
            else:
                print("Admin user already exists!")
                
            # Print the database path for verification
            print(f"Using database at: {db_path}")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000) 