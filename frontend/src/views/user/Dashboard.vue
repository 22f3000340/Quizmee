<template>
  <div class="user-dashboard">
    <h1 class="mb-4">My Dashboard</h1>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading dashboard data...</p>
    </div>
    
    <div v-else>
      <div class="row mb-4">
        <div class="col-md-4 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5 class="card-title">Subjects Available</h5>
              <h2 class="display-4">{{ stats.subjects }}</h2>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <span>Browse all subjects</span>
              <router-link :to="{name: 'UserSubjects'}" class="btn btn-light btn-sm">
                View All
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Quizzes Attempted</h5>
              <h2 class="display-4">{{ stats.quizzesAttempted }}</h2>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <span>View your progress</span>
              <router-link :to="{name: 'UserScores'}" class="btn btn-light btn-sm">
                View All
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h5 class="card-title">Average Score</h5>
              <h2 class="display-4">{{ stats.averageScore }}%</h2>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <span>Keep improving!</span>
              <router-link :to="{name: 'UserScores'}" class="btn btn-light btn-sm">
                View Details
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-8 mb-4">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0">Recent Scores</h5>
            </div>
            <div class="card-body">
              <div v-if="stats.recentScores.length === 0" class="text-center py-5">
                <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                <h5>No Quiz Attempts Yet</h5>
                <p class="text-muted">Take a quiz to start tracking your progress!</p>
                <router-link :to="{name: 'UserSubjects'}" class="btn btn-primary mt-2">
                  Browse Subjects
                </router-link>
              </div>
              <div v-else>
                <div class="table-responsive">
                  <table class="table">
                    <thead>
                      <tr>
                        <th>Quiz Name</th>
                        <th>Date</th>
                        <th>Score</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="score in stats.recentScores" :key="score.id">
                        <td>{{ score.quizName }}</td>
                        <td>{{ formatDate(score.date) }}</td>
                        <td>{{ score.score }}%</td>
                        <td>
                          <span :class="getScoreBadgeClass(score.score)">
                            {{ getScoreLabel(score.score) }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-4 mb-4">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0">Subject Progress</h5>
            </div>
            <div class="card-body">
              <div v-if="stats.subjectProgress.length === 0" class="text-center py-5">
                <i class="fas fa-book fa-3x text-muted mb-3"></i>
                <h5>No Progress Yet</h5>
                <p class="text-muted">Take quizzes to see your progress by subject!</p>
              </div>
              <div v-else>
                <div v-for="subject in stats.subjectProgress" :key="subject.id" class="mb-3">
                  <div class="d-flex justify-content-between">
                    <span>{{ subject.name }}</span>
                    <span>{{ subject.progress }}%</span>
                  </div>
                  <div class="progress" style="height: 10px;">
                    <div class="progress-bar" role="progressbar" 
                         :style="{ width: subject.progress + '%', backgroundColor: getProgressColor(subject.progress) }" 
                         :aria-valuenow="subject.progress" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card shadow mt-4">
            <div class="card-header">
              <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <router-link :to="{name: 'UserSubjects'}" class="btn btn-primary">
                  <i class="fas fa-book me-2"></i> Browse Subjects
                </router-link>
                <router-link :to="{name: 'UserScores'}" class="btn btn-success">
                  <i class="fas fa-chart-line me-2"></i> View All Scores
                </router-link>
              </div>
            </div>
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
  name: 'UserDashboard',
  data() {
    return {
      loading: true,
      error: null,
      stats: {
        subjects: 0,
        quizzesAttempted: 0,
        averageScore: 0,
        recentScores: [],
        subjectProgress: []
      }
    }
  },
  mounted() {
    this.fetchDashboardData();
  },
  methods: {
    async fetchDashboardData() {
      try {
        const response = await ApiService.get(API_CONFIG.ENDPOINTS.SCORES);
        
        // Prepare data for display
        this.stats = {
          subjects: response.subjects_count || 0,
          quizzesAttempted: response.attempts_count || 0,
          averageScore: response.average_score || 0,
          recentScores: response.recent_scores || [],
          subjectProgress: response.subject_progress || []
        };
        
        this.loading = false;
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        this.error = error.message || 'Failed to load dashboard data';
        this.loading = false;
      }
    },
    
    formatDate(date) {
      if (!date) return '';
      
      try {
        // Handle ISO strings from API (which are in UTC time)
        let dateObj;
        
        if (typeof date === 'string') {
          // Check if the string has timezone info
          if (date.endsWith('Z') || date.includes('+')) {
            // Already has timezone info
            dateObj = new Date(date);
          } else {
            // Assume UTC time from backend API
            dateObj = new Date(date + 'Z');
          }
        } else {
          dateObj = date;
        }
        
        return dateObj.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (err) {
        console.error('Error formatting date:', err);
        return typeof date === 'string' ? date : '';
      }
    },
    
    getScoreBadgeClass(score) {
      if (score >= 90) return 'badge bg-success';
      if (score >= 70) return 'badge bg-info';
      if (score >= 50) return 'badge bg-warning';
      return 'badge bg-danger';
    },
    
    getScoreLabel(score) {
      if (score >= 90) return 'Excellent';
      if (score >= 70) return 'Good';
      if (score >= 50) return 'Average';
      return 'Needs Improvement';
    },
    
    getProgressColor(progress) {
      if (progress >= 80) return '#28a745'; // Success
      if (progress >= 60) return '#17a2b8'; // Info
      if (progress >= 40) return '#ffc107'; // Warning
      return '#dc3545'; // Danger
    }
  }
}
</script>

<style scoped>
.progress {
  background-color: #f5f5f5;
}
</style> 