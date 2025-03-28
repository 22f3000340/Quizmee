<template>
  <div class="user-quizzes">
    <h1 class="mb-4">Available Quizzes</h1>
    <h3 class="mb-3">Chapter: {{ chapterName }}</h3>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading quizzes...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i> {{ error }}
    </div>
    
    <!-- No quizzes available -->
    <div v-else-if="quizzes.length === 0" class="text-center py-5">
      <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
      <h3>No Quizzes Available</h3>
      <p class="text-muted">This chapter has no quizzes yet.</p>
      <router-link v-if="subjectId" :to="{name: 'UserChapters', params: {subjectId: subjectId}}" class="btn btn-primary mt-2">
        <i class="fas fa-arrow-left me-2"></i> Back to Chapters
      </router-link>
      <router-link v-else :to="{name: 'UserSubjects'}" class="btn btn-primary mt-2">
        <i class="fas fa-arrow-left me-2"></i> Back to Subjects
      </router-link>
    </div>
    
    <!-- Quizzes list -->
    <div v-else class="row">
      <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title">{{ quiz.title }}</h5>
            <p class="card-text text-muted">{{ quiz.description }}</p>
            <div class="d-flex justify-content-between mb-3">
              <span class="badge bg-info">
                <i class="fas fa-clock me-1"></i> {{ quiz.duration }} mins
              </span>
              <span class="badge bg-secondary">
                <i class="fas fa-question me-1"></i> {{ getQuestionCount(quiz) }} Questions
              </span>
            </div>
          </div>
          <div class="card-footer bg-white border-top-0">
            <router-link :to="{name: 'TakeQuiz', params: {quizId: quiz.id}}" class="btn btn-success w-100">
              <i class="fas fa-play-circle me-2"></i> Take Quiz
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Back to Chapters button -->
    <div class="mt-4">
      <router-link v-if="subjectId" :to="{name: 'UserChapters', params: {subjectId: subjectId}}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left me-2"></i> Back to Chapters
      </router-link>
      <router-link v-else :to="{name: 'UserSubjects'}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left me-2"></i> Back to Subjects
      </router-link>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'UserQuizzes',
  props: {
    chapterId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      chapterName: '',
      subjectId: null,
      quizzes: [],
      loading: true,
      error: null
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        // First, get the chapter details to get the name and subject ID
        const chapterData = await ApiService.get(API_CONFIG.ENDPOINTS.CHAPTER_BY_ID(this.chapterId));
        this.chapterName = chapterData.name;
        this.subjectId = chapterData.subject_id;
        
        // Then, get the quizzes for this chapter
        // Add timestamp to prevent caching
        const timestamp = new Date().getTime();
        const quizzesEndpoint = API_CONFIG.ENDPOINTS.QUIZZES(this.chapterId);
        console.log('Fetching quizzes from:', quizzesEndpoint);
        
        const quizzesData = await ApiService.get(quizzesEndpoint, { _t: timestamp });
        console.log('API Response:', quizzesData);
        
        this.quizzes = quizzesData.quizzes || quizzesData;
        console.log('Quizzes array before processing:', this.quizzes);
        
        // Explicitly transform the data to ensure question_count is available
        if (this.quizzes && this.quizzes.length > 0) {
          this.quizzes = this.quizzes.map(quiz => {
            // Make sure question_count is properly assigned and is a number
            const questionCount = quiz.question_count !== undefined ? Number(quiz.question_count) : 0;
            
            return {
              ...quiz,
              question_count: questionCount
            };
          });
        }
        
        console.log('Quizzes array after processing:', this.quizzes);
        
        // Log each quiz for debugging
        if (this.quizzes && this.quizzes.length > 0) {
          this.quizzes.forEach((quiz, index) => {
            console.log(`Quiz ${index + 1} (${quiz.id}):`, {
              title: quiz.title,
              description: quiz.description,
              questionCount: quiz.questionCount,
              question_count: quiz.question_count
            });
          });
        }
      } catch (error) {
        console.error('Error loading quizzes:', error);
        this.error = error.message || 'Failed to load quizzes';
      } finally {
        this.loading = false;
      }
    },
    getQuestionCount(quiz) {
      // For debugging
      console.log('Quiz question count:', quiz.id, quiz.question_count);
      
      // Return the question count or 0 if not available
      return quiz.question_count || 0;
    }
  }
}
</script> 