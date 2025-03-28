# Quiz Master V2 API Documentation

This document provides details about the available API endpoints for the Quiz Master V2 application.

## Base URL

All endpoints are relative to: `http://localhost:5000/api`

## Authentication

Most endpoints require JWT authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Login

- **URL**: `/login`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "username": "username",
    "password": "password"
  }
  ```
- **Success Response**: Status Code 200
  ```json
  {
    "access_token": "jwt_token_here",
    "user": {
      "id": 1,
      "username": "username",
      "full_name": "Full Name",
      "email": "email@example.com",
      "is_admin": false
    }
  }
  ```
- **Error Response**: Status Code 401
  ```json
  {
    "msg": "Invalid username or password"
  }
  ```

#### Register

- **URL**: `/register`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "username": "username",
    "email": "email@example.com",
    "full_name": "Full Name",
    "qualification": "Qualification",
    "date_of_birth": "YYYY-MM-DD",
    "password": "password"
  }
  ```
- **Success Response**: Status Code 201
  ```json
  {
    "msg": "User registered successfully"
  }
  ```
- **Error Response**: Status Code 400
  ```json
  {
    "msg": "Username already exists"
  }
  ```

### Users

#### Get Users (Admin Only)

- **URL**: `/users`
- **Method**: `GET`
- **Auth Required**: Yes (Admin)
- **Success Response**: Status Code 200
  ```json
  {
    "users": [
      {
        "id": 1,
        "username": "username",
        "full_name": "Full Name",
        "email": "email@example.com",
        "qualification": "Qualification",
        "date_of_birth": "YYYY-MM-DD"
      }
    ]
  }
  ```

### Subjects

#### Get All Subjects

- **URL**: `/subjects`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: Status Code 200
  ```json
  {
    "subjects": [
      {
        "id": 1,
        "name": "Subject Name",
        "description": "Subject description"
      }
    ]
  }
  ```

#### Create Subject (Admin Only)

- **URL**: `/subjects`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "name": "Subject Name",
    "description": "Subject description"
  }
  ```
- **Success Response**: Status Code 201
  ```json
  {
    "id": 1,
    "name": "Subject Name",
    "description": "Subject description"
  }
  ```

#### Update Subject (Admin Only)

- **URL**: `/subjects/:subject_id`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "name": "Updated Subject Name",
    "description": "Updated subject description"
  }
  ```
- **Success Response**: Status Code 200
  ```json
  {
    "id": 1,
    "name": "Updated Subject Name",
    "description": "Updated subject description"
  }
  ```

#### Delete Subject (Admin Only)

- **URL**: `/subjects/:subject_id`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: Status Code 200
  ```json
  {
    "msg": "Subject deleted successfully"
  }
  ```

### Chapters

#### Get Chapters for a Subject

- **URL**: `/subjects/:subject_id/chapters`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: Status Code 200
  ```json
  {
    "chapters": [
      {
        "id": 1,
        "name": "Chapter Name",
        "description": "Chapter description",
        "subject_id": 1
      }
    ]
  }
  ```

#### Create Chapter (Admin Only)

- **URL**: `/subjects/:subject_id/chapters`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "name": "Chapter Name",
    "description": "Chapter description"
  }
  ```
- **Success Response**: Status Code 201
  ```json
  {
    "id": 1,
    "name": "Chapter Name",
    "description": "Chapter description",
    "subject_id": 1
  }
  ```

#### Update Chapter (Admin Only)

- **URL**: `/chapters/:chapter_id`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "name": "Updated Chapter Name",
    "description": "Updated chapter description"
  }
  ```
- **Success Response**: Status Code 200
  ```json
  {
    "id": 1,
    "name": "Updated Chapter Name",
    "description": "Updated chapter description",
    "subject_id": 1
  }
  ```

#### Delete Chapter (Admin Only)

- **URL**: `/chapters/:chapter_id`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: Status Code 200
  ```json
  {
    "msg": "Chapter deleted successfully"
  }
  ```

### Quizzes

#### Get Quizzes for a Chapter

- **URL**: `/chapters/:chapter_id/quizzes`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: Status Code 200
  ```json
  {
    "quizzes": [
      {
        "id": 1,
        "title": "Quiz Title",
        "chapter_id": 1,
        "duration": 30,
        "date_of_quiz": "YYYY-MM-DD HH:MM:SS",
        "remarks": "Quiz remarks"
      }
    ]
  }
  ```

#### Create Quiz (Admin Only)

- **URL**: `/chapters/:chapter_id/quizzes`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "title": "Quiz Title",
    "duration": 30,
    "date_of_quiz": "YYYY-MM-DD HH:MM:SS",
    "remarks": "Quiz remarks"
  }
  ```
- **Success Response**: Status Code 201
  ```json
  {
    "id": 1,
    "title": "Quiz Title",
    "chapter_id": 1,
    "duration": 30,
    "date_of_quiz": "YYYY-MM-DD HH:MM:SS",
    "remarks": "Quiz remarks"
  }
  ```

#### Update Quiz (Admin Only)

- **URL**: `/quizzes/:quiz_id`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "title": "Updated Quiz Title",
    "duration": 45,
    "date_of_quiz": "YYYY-MM-DD HH:MM:SS",
    "remarks": "Updated quiz remarks"
  }
  ```
- **Success Response**: Status Code 200
  ```json
  {
    "id": 1,
    "title": "Updated Quiz Title",
    "chapter_id": 1,
    "duration": 45,
    "date_of_quiz": "YYYY-MM-DD HH:MM:SS",
    "remarks": "Updated quiz remarks"
  }
  ```

#### Delete Quiz (Admin Only)

- **URL**: `/quizzes/:quiz_id`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: Status Code 200
  ```json
  {
    "msg": "Quiz deleted successfully"
  }
  ```

### Questions

#### Get Questions for a Quiz

- **URL**: `/quizzes/:quiz_id/questions`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response for Admin**: Status Code 200
  ```json
  {
    "questions": [
      {
        "id": 1,
        "quiz_id": 1,
        "question_text": "Question text",
        "option1": "Option 1",
        "option2": "Option 2",
        "option3": "Option 3",
        "option4": "Option 4",
        "correct_option": 1
      }
    ]
  }
  ```
- **Success Response for User**: Status Code 200 (Note: `correct_option` is omitted)
  ```json
  {
    "questions": [
      {
        "id": 1,
        "quiz_id": 1,
        "question_text": "Question text",
        "option1": "Option 1",
        "option2": "Option 2",
        "option3": "Option 3",
        "option4": "Option 4"
      }
    ]
  }
  ```

#### Create Question (Admin Only)

- **URL**: `/quizzes/:quiz_id/questions`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "question_text": "Question text",
    "option1": "Option 1",
    "option2": "Option 2",
    "option3": "Option 3",
    "option4": "Option 4",
    "correct_option": 1
  }
  ```
- **Success Response**: Status Code 201
  ```json
  {
    "id": 1,
    "quiz_id": 1,
    "question_text": "Question text",
    "option1": "Option 1",
    "option2": "Option 2",
    "option3": "Option 3",
    "option4": "Option 4",
    "correct_option": 1
  }
  ```

#### Update Question (Admin Only)

- **URL**: `/questions/:question_id`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
  ```json
  {
    "question_text": "Updated question text",
    "option1": "Updated option 1",
    "option2": "Updated option 2",
    "option3": "Updated option 3",
    "option4": "Updated option 4",
    "correct_option": 2
  }
  ```
- **Success Response**: Status Code 200
  ```json
  {
    "id": 1,
    "quiz_id": 1,
    "question_text": "Updated question text",
    "option1": "Updated option 1",
    "option2": "Updated option 2",
    "option3": "Updated option 3",
    "option4": "Updated option 4",
    "correct_option": 2
  }
  ```

#### Delete Question (Admin Only)

- **URL**: `/questions/:question_id`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: Status Code 200
  ```json
  {
    "msg": "Question deleted successfully"
  }
  ```

### Quiz Attempts

#### Submit Quiz Attempt

- **URL**: `/quizzes/:quiz_id/attempt`
- **Method**: `POST`
- **Auth Required**: Yes
- **Body**:
  ```json
  {
    "answers": {
      "1": 2,
      "2": 1,
      "3": 3
    },
    "time_taken": 1200
  }
  ```
  Note: The keys in the `answers` object are question IDs, and the values are the selected option numbers.
- **Success Response**: Status Code 201
  ```json
  {
    "id": 1,
    "quiz_id": 1,
    "score": 66.67,
    "total_questions": 3,
    "correct_answers": 2,
    "time_taken": 1200,
    "timestamp": "YYYY-MM-DD HH:MM:SS"
  }
  ```

### User Scores

#### Get User's Scores

- **URL**: `/users/scores`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: Status Code 200
  ```json
  {
    "scores": [
      {
        "id": 1,
        "quiz_id": 1,
        "quiz_title": "Quiz Title",
        "chapter_name": "Chapter Name",
        "subject_name": "Subject Name",
        "score": 75.0,
        "total_questions": 4,
        "correct_answers": 3,
        "time_taken": 1500,
        "timestamp": "YYYY-MM-DD HH:MM:SS"
      }
    ]
  }
  ```

### Admin Statistics

#### Get Admin Statistics

- **URL**: `/admin/statistics`
- **Method**: `GET`
- **Auth Required**: Yes (Admin)
- **Success Response**: Status Code 200
  ```json
  {
    "counts": {
      "users": 10,
      "subjects": 5,
      "chapters": 15,
      "quizzes": 25,
      "questions": 100,
      "attempts": 50
    },
    "subject_scores": [
      {
        "subject_name": "Subject Name",
        "avg_score": 78.5,
        "attempts": 20
      }
    ]
  }
  ``` 