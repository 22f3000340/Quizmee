<template>
  <div class="user-chapters">
    <h1 class="mb-4">Browse Chapters</h1>
    <h3 class="mb-3">Subject: {{ subjectName }}</h3>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading chapters...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i> {{ error }}
    </div>
    
    <!-- No chapters available -->
    <div v-else-if="chapters.length === 0" class="text-center py-5">
      <i class="fas fa-book-open fa-3x text-muted mb-3"></i>
      <h3>No Chapters Available</h3>
      <p class="text-muted">This subject has no chapters yet.</p>
      <router-link :to="{name: 'UserSubjects'}" class="btn btn-primary mt-2">
        <i class="fas fa-arrow-left me-2"></i> Back to Subjects
      </router-link>
    </div>
    
    <!-- Chapters list -->
    <div v-else class="row">
      <div v-for="chapter in chapters" :key="chapter.id" class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title">{{ chapter.name }}</h5>
            <p class="card-text text-muted">{{ chapter.description }}</p>
          </div>
          <div class="card-footer bg-white border-top-0">
            <router-link :to="{name: 'UserQuizzes', params: {chapterId: chapter.id}}" class="btn btn-primary w-100">
              <i class="fas fa-list me-2"></i> View Quizzes
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Back to Subjects button -->
    <div class="mt-4">
      <router-link :to="{name: 'UserSubjects'}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left me-2"></i> Back to Subjects
      </router-link>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'UserChapters',
  props: {
    subjectId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      subjectName: '',
      chapters: [],
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
        // First, get the subject details
        const subjectResponse = await ApiService.get(API_CONFIG.ENDPOINTS.SUBJECT_BY_ID(this.subjectId));
        this.subjectName = subjectResponse.name;
        
        // Then, get the chapters for this subject
        const chaptersResponse = await ApiService.get(API_CONFIG.ENDPOINTS.CHAPTERS(this.subjectId));
        this.chapters = chaptersResponse.chapters || chaptersResponse;
      } catch (error) {
        console.error('Error loading chapters:', error);
        this.error = error.message || 'Failed to load chapters';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 