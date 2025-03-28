<template>
  <div class="user-subjects">
    <h1 class="mb-4">Browse Subjects</h1>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading subjects...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i> {{ error }}
    </div>
    
    <!-- No subjects available -->
    <div v-else-if="subjects.length === 0" class="text-center py-5">
      <i class="fas fa-book fa-3x text-muted mb-3"></i>
      <h3>No Subjects Available</h3>
      <p class="text-muted">Please check back later for available subjects.</p>
    </div>
    
    <!-- Subjects list -->
    <div v-else class="row">
      <div v-for="subject in subjects" :key="subject.id" class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title">{{ subject.name }}</h5>
            <p class="card-text text-muted">{{ subject.description }}</p>
          </div>
          <div class="card-footer bg-white border-top-0">
            <router-link :to="{name: 'UserChapters', params: {subjectId: subject.id}}" class="btn btn-primary w-100">
              <i class="fas fa-book-open me-2"></i> View Chapters
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'UserSubjects',
  data() {
    return {
      subjects: [],
      loading: true,
      error: null
    }
  },
  mounted() {
    this.fetchSubjects();
  },
  methods: {
    async fetchSubjects() {
      try {
        // Get subjects from the backend
        const response = await ApiService.get(API_CONFIG.ENDPOINTS.SUBJECTS);
        this.subjects = response.subjects || response;
      } catch (error) {
        console.error('Error loading subjects:', error);
        this.error = error.message || 'Failed to load subjects';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 