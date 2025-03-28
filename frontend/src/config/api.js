const API_CONFIG = {
  BASE_URL: 'http://localhost:5000/api',
  TIMEOUT: 10000, // 10 seconds
  ENDPOINTS: {
    // Auth
    LOGIN: '/login',
    REGISTER: '/register',
    
    // User
    SCORES: '/users/scores',
    USER_PROFILE: '/profile',
    
    // Content
    SUBJECTS: '/subjects',
    SUBJECT_BY_ID: (id) => `/subjects/${id}`,
    CHAPTERS: (subjectId) => `/subjects/${subjectId}/chapters`,
    CHAPTER_BY_ID: (id) => `/chapters/${id}`,
    QUIZZES: (chapterId) => `/chapters/${chapterId}/quizzes`,
    QUIZ_BY_ID: (id) => `/quizzes/${id}`,
    QUESTIONS: (quizId) => `/quizzes/${quizId}/questions`,
    QUESTION_BY_ID: (id) => `/questions/${id}`,
    QUIZ_ATTEMPT: (quizId) => `/quizzes/${quizId}/attempt`,
    
    // Admin
    USERS: '/users',
    ADMIN_STATS: '/admin/statistics'
  }
};

export default API_CONFIG; 