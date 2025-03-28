<template>
  <div class="user-scores">
    <h1 class="mb-4">My Scores</h1>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your scores...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i> {{ error }}
    </div>
    
    <!-- No scores yet -->
    <div v-else-if="scores.length === 0" class="text-center py-5">
      <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
      <h3>No Quiz Attempts Yet</h3>
      <p class="text-muted">Take a quiz to start tracking your progress!</p>
      <router-link :to="{name: 'UserSubjects'}" class="btn btn-primary mt-2">
        Browse Subjects
      </router-link>
    </div>
    
    <!-- Scores data -->
    <div v-else>
      <div class="card shadow mb-4">
        <div class="card-header">
          <h5 class="mb-0">Performance Summary</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-8">
              <div v-if="scores.length > 0" style="position: relative; height: 300px;">
                <div id="chart-container" style="width: 100%; height: 100%;">
                  <!-- Chart will be rendered here -->
                </div>
              </div>
              <div v-else class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i> No score history to display yet
              </div>
            </div>
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h5 class="card-title">Average Score</h5>
                  <h2 class="display-4" :class="getScoreColorClass(averageScore)">
                    {{ averageScore.toFixed(1) }}%
                  </h2>
                  <p class="text-muted mb-0">
                    {{ scores.length }} quiz{{ scores.length !== 1 ? 'zes' : '' }} attempted
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card shadow">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Quiz History</h5>
          <button class="btn btn-sm btn-primary" @click="fetchScores">
            <i class="fas fa-sync-alt me-1"></i> Refresh
          </button>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Quiz</th>
                  <th>Chapter</th>
                  <th>Subject</th>
                  <th>Score</th>
                  <th>Time Taken</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="score in sortedScores" :key="score.id">
                  <td>{{ formatDate(score.timestamp) }}</td>
                  <td>{{ score.quiz_title }}</td>
                  <td>{{ score.chapter_name }}</td>
                  <td>{{ score.subject_name }}</td>
                  <td>
                    <span :class="getScoreBadgeClass(score.score)">
                      {{ score.score.toFixed(1) }}%
                    </span>
                  </td>
                  <td>{{ formatTime(score.time_taken) }}</td>
                </tr>
              </tbody>
            </table>
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
  name: 'UserScores',
  data() {
    return {
      scores: [],
      loading: true,
      error: null,
      chart: null
    }
  },
  computed: {
    sortedScores() {
      // Sort scores by timestamp (newest first)
      return [...this.scores].sort((a, b) => {
        return new Date(b.timestamp) - new Date(a.timestamp);
      });
    },
    averageScore() {
      if (this.scores.length === 0) return 0;
      const sum = this.scores.reduce((acc, score) => acc + score.score, 0);
      return sum / this.scores.length;
    }
  },
  mounted() {
    this.fetchScores();
    
    // Add a script tag to ensure Chart.js is loaded properly (if not already present)
    const chartScriptId = 'chartjs-script';
    if (!document.getElementById(chartScriptId) && typeof Chart === 'undefined') {
      const script = document.createElement('script');
      script.id = chartScriptId;
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js';
      script.integrity = 'sha256-Y26AMvaIfrZ1EQU49pf6H4QzVTrOI8m9wQYKkftBt4s=';
      script.crossOrigin = 'anonymous';
      script.onload = () => {
        console.log('Chart.js loaded dynamically');
        if (this.scores.length > 0) {
          this.renderChart();
        }
      };
      document.head.appendChild(script);
    }
  },
  methods: {
    async fetchScores() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await ApiService.get(API_CONFIG.ENDPOINTS.SCORES);
        this.scores = response.scores || [];
        this.loading = false;
        
        // Give time for the DOM to update
        setTimeout(() => {
          this.renderChart();
        }, 500); // Longer timeout for stability
      } catch (error) {
        console.error('Error fetching scores:', error);
        this.error = error.message || 'Failed to load scores';
        this.loading = false;
      }
    },
    
    renderChart() {
      // Skip if no scores or Chart is not available
      if (this.scores.length === 0) return;
      if (typeof Chart === 'undefined') {
        console.log('Chart.js not available yet, waiting...');
        return;
      }
      
      // Get container element
      const container = document.getElementById('chart-container');
      if (!container) {
        console.error('Chart container not found');
        return;
      }
      
      // Destroy existing chart if it exists
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
      
      // Clear any existing content
      container.innerHTML = '';
      
      try {
        // Create canvas element
        const canvas = document.createElement('canvas');
        canvas.id = 'score-chart';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        
        // Add to container
        container.appendChild(canvas);
        
        // Handle DPI scaling for canvas (important for clarity)
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        
        // Get the 2D context
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
        
        // Prepare data - use last 10 scores or fewer if not available
        const recentScores = [...this.scores].sort((a, b) => {
          return new Date(a.timestamp) - new Date(b.timestamp);
        }).slice(-10);
        
        const labels = recentScores.map(s => s.quiz_title);
        const data = recentScores.map(s => s.score);
        
        console.log('Rendering chart with data:', {labels, data});
        
        // Create chart
        this.chart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: 'Quiz Scores (%)',
              data: data,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2,
              pointRadius: 5,
              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
              tension: 0.1,
              fill: true
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                min: 0,
                max: 100,
                title: {
                  display: true,
                  text: 'Score (%)'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Quizzes'
                }
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `Score: ${context.formattedValue}%`;
                  }
                }
              },
              legend: {
                display: true,
                position: 'top'
              }
            }
          }
        });
        
        console.log('Chart rendered successfully');
      } catch (error) {
        console.error('Error rendering chart:', error);
        // Fallback to a table if chart fails
        this.renderFallbackTable(container);
      }
    },
    
    renderFallbackTable(container) {
      // Create a fallback table if the chart fails
      container.innerHTML = `
        <h5 class="mb-3">Recent Quiz Performance</h5>
        <div class="table-responsive">
          <table class="table table-sm">
            <thead>
              <tr>
                <th>Quiz</th>
                <th>Date</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              ${this.scores.slice(-5).map(score => `
                <tr>
                  <td>${score.quiz_title}</td>
                  <td>${this.formatDate(score.timestamp)}</td>
                  <td>
                    <span class="${this.getScoreBadgeClass(score.score)}">
                      ${score.score.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        // Handle ISO strings from API (which are in UTC time)
        let date;
        
        if (typeof dateString === 'string') {
          // Check if the string has timezone info
          if (dateString.endsWith('Z') || dateString.includes('+')) {
            // Already has timezone info
            date = new Date(dateString);
          } else {
            // Assume UTC time from backend API
            date = new Date(dateString + 'Z'); 
          }
        } else {
          date = dateString;
        }
        
        return date.toLocaleString('en-US', { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (err) {
        console.error('Error formatting date:', err);
        return dateString;
      }
    },
    
    formatTime(seconds) {
      if (!seconds) return '0s';
      
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      
      if (minutes === 0) {
        return `${remainingSeconds}s`;
      } else if (remainingSeconds === 0) {
        return `${minutes}m`;
      } else {
        return `${minutes}m ${remainingSeconds}s`;
      }
    },
    
    getScoreBadgeClass(score) {
      if (score >= 90) return 'badge bg-success';
      if (score >= 70) return 'badge bg-info';
      if (score >= 50) return 'badge bg-warning';
      return 'badge bg-danger';
    },
    
    getScoreColorClass(score) {
      if (score >= 90) return 'text-success';
      if (score >= 70) return 'text-info';
      if (score >= 50) return 'text-warning';
      return 'text-danger';
    }
  }
}
</script>

<style scoped>
.card {
  margin-bottom: 1.5rem;
}
</style> 