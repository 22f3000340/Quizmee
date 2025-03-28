# Quiz Master V2 API Documentation

## Base URL
All endpoints are relative to: `http://localhost:5000/api`

## Authentication
Most endpoints require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## API Endpoints

### Authentication

#### Login
- **URL**: `/login`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
```json
{
  "username": "string",
  "password": "string"
}
```
- **Success Response**: 200 OK
```json
{
  "access_token": "string",
  "user": {
    "id": "integer",
    "username": "string",
    "full_name": "string",
    "email": "string",
    "is_admin": "boolean"
  }
}
```

#### Register
- **URL**: `/register`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
```json
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "qualification": "string",
  "date_of_birth": "YYYY-MM-DD",
  "password": "string"
}
```
- **Success Response**: 201 Created
```json
{
  "msg": "User registered successfully"
}
```

### Users

#### Get All Users (Admin Only)
- **URL**: `/users`
- **Method**: `GET`
- **Auth Required**: Yes (Admin)
- **Success Response**: 200 OK
```json
{
  "users": [
    {
      "id": "integer",
      "username": "string",
      "full_name": "string",
      "email": "string",
      "qualification": "string",
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
- **Success Response**: 200 OK
```json
{
  "subjects": [
    {
      "id": "integer",
      "name": "string",
      "description": "string"
    }
  ]
}
```

#### Get Subject by ID
- **URL**: `/subjects/{subject_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: 200 OK
```json
{
  "id": "integer",
  "name": "string",
  "description": "string"
}
```

#### Create Subject (Admin Only)
- **URL**: `/subjects`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "name": "string",
  "description": "string"
}
```
- **Success Response**: 201 Created
```json
{
  "id": "integer",
  "name": "string",
  "description": "string"
}
```

#### Update Subject (Admin Only)
- **URL**: `/subjects/{subject_id}`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "name": "string",
  "description": "string"
}
```
- **Success Response**: 200 OK
```json
{
  "id": "integer",
  "name": "string",
  "description": "string"
}
```

#### Delete Subject (Admin Only)
- **URL**: `/subjects/{subject_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: 200 OK
```json
{
  "msg": "Subject deleted successfully"
}
```

### Chapters

#### Get Chapters by Subject
- **URL**: `/subjects/{subject_id}/chapters`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: 200 OK
```json
{
  "chapters": [
    {
      "id": "integer",
      "name": "string",
      "description": "string",
      "subject_id": "integer"
    }
  ]
}
```

#### Create Chapter (Admin Only)
- **URL**: `/subjects/{subject_id}/chapters`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "name": "string",
  "description": "string"
}
```
- **Success Response**: 201 Created
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "subject_id": "integer"
}
```

#### Get Chapter by ID
- **URL**: `/chapters/{chapter_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: 200 OK
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "subject_id": "integer"
}
```

#### Update Chapter (Admin Only)
- **URL**: `/chapters/{chapter_id}`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "name": "string",
  "description": "string"
}
```
- **Success Response**: 200 OK
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "subject_id": "integer"
}
```

#### Delete Chapter (Admin Only)
- **URL**: `/chapters/{chapter_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: 200 OK
```json
{
  "msg": "Chapter deleted successfully"
}
```

### Quizzes

#### Get Quizzes by Chapter
- **URL**: `/chapters/{chapter_id}/quizzes`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: 200 OK
```json
{
  "quizzes": [
    {
      "id": "integer",
      "title": "string",
      "description": "string",
      "chapter_id": "integer",
      "time_limit": "integer",
      "passing_score": "integer"
    }
  ]
}
```

#### Create Quiz (Admin Only)
- **URL**: `/chapters/{chapter_id}/quizzes`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "title": "string",
  "description": "string",
  "time_limit": "integer",
  "passing_score": "integer"
}
```
- **Success Response**: 201 Created
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "chapter_id": "integer",
  "time_limit": "integer",
  "passing_score": "integer"
}
```

#### Get Quiz by ID
- **URL**: `/quizzes/{quiz_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: 200 OK
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "chapter_id": "integer",
  "time_limit": "integer",
  "passing_score": "integer"
}
```

#### Update Quiz (Admin Only)
- **URL**: `/quizzes/{quiz_id}`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "title": "string",
  "description": "string",
  "time_limit": "integer",
  "passing_score": "integer"
}
```
- **Success Response**: 200 OK
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "chapter_id": "integer",
  "time_limit": "integer",
  "passing_score": "integer"
}
```

#### Delete Quiz (Admin Only)
- **URL**: `/quizzes/{quiz_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: 200 OK
```json
{
  "msg": "Quiz deleted successfully"
}
```

### Questions

#### Get Questions by Quiz
- **URL**: `/quizzes/{quiz_id}/questions`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: 200 OK
```json
{
  "questions": [
    {
      "id": "integer",
      "quiz_id": "integer",
      "question_text": "string",
      "option_a": "string",
      "option_b": "string",
      "option_c": "string",
      "option_d": "string",
      "correct_option": "string"
    }
  ]
}
```

#### Create Question (Admin Only)
- **URL**: `/quizzes/{quiz_id}/questions`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "question_text": "string",
  "option_a": "string",
  "option_b": "string",
  "option_c": "string",
  "option_d": "string",
  "correct_option": "string"
}
```
- **Success Response**: 201 Created
```json
{
  "id": "integer",
  "quiz_id": "integer",
  "question_text": "string",
  "option_a": "string",
  "option_b": "string",
  "option_c": "string",
  "option_d": "string",
  "correct_option": "string"
}
```

#### Update Question (Admin Only)
- **URL**: `/questions/{question_id}`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin)
- **Body**:
```json
{
  "question_text": "string",
  "option_a": "string",
  "option_b": "string",
  "option_c": "string",
  "option_d": "string",
  "correct_option": "string"
}
```
- **Success Response**: 200 OK
```json
{
  "id": "integer",
  "quiz_id": "integer",
  "question_text": "string",
  "option_a": "string",
  "option_b": "string",
  "option_c": "string",
  "option_d": "string",
  "correct_option": "string"
}
```

#### Delete Question (Admin Only)
- **URL**: `/questions/{question_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin)
- **Success Response**: 200 OK
```json
{
  "msg": "Question deleted successfully"
}
```

### Quiz Attempts

#### Submit Quiz Attempt
- **URL**: `/quizzes/{quiz_id}/attempt`
- **Method**: `POST`
- **Auth Required**: Yes
- **Body**:
```json
{
  "answers": [
    {
      "question_id": "integer",
      "selected_option": "string"
    }
  ]
}
```
- **Success Response**: 200 OK
```json
{
  "score": "integer",
  "total_questions": "integer",
  "correct_answers": "integer",
  "time_taken": "integer",
  "passed": "boolean"
}
```

### User Scores

#### Get User Scores
- **URL**: `/users/scores`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: 200 OK
```json
{
  "scores": [
    {
      "id": "integer",
      "user_id": "integer",
      "quiz_id": "integer",
      "score": "integer",
      "total_questions": "integer",
      "correct_answers": "integer",
      "time_taken": "integer",
      "passed": "boolean",
      "attempt_date": "datetime"
    }
  ]
}
```

### Admin Statistics

#### Get Admin Statistics (Admin Only)
- **URL**: `/admin/statistics`
- **Method**: `GET`
- **Auth Required**: Yes (Admin)
- **Success Response**: 200 OK
```json
{
  "total_users": "integer",
  "total_subjects": "integer",
  "total_chapters": "integer",
  "total_quizzes": "integer",
  "total_questions": "integer",
  "total_attempts": "integer",
  "average_scores": {
    "subject_id": "float"
  },
  "passing_rates": {
    "subject_id": "float"
  }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "msg": "Error message"
}
```

### 401 Unauthorized
```json
{
  "msg": "Invalid username or password"
}
```

### 403 Forbidden
```json
{
  "msg": "Admin privileges required"
}
```

### 404 Not Found
```json
{
  "msg": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "msg": "Internal server error"
}
``` 