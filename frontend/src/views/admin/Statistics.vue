<template>
  <div class="admin-statistics">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="mb-0">Statistics</h1>
      <button class="btn btn-primary" @click="refreshStatistics">
        <i class="fas fa-sync-alt me-1"></i> Refresh
      </button>
    </div>
    
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <div class="card shadow mb-4">
      <div class="card-header">
        <h5 class="mb-0">Summary</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading statistics...</p>
        </div>
        
        <div v-else class="row g-4">
          <div class="col-md-3">
            <div class="card text-center bg-primary text-white">
              <div class="card-body">
                <h2>{{ stats.counts.users || 0 }}</h2>
                <p class="mb-0">Total Users</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card text-center bg-success text-white">
              <div class="card-body">
                <h2>{{ stats.counts.subjects || 0 }}</h2>
                <p class="mb-0">Subjects</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card text-center bg-info text-white">
              <div class="card-body">
                <h2>{{ stats.counts.quizzes || 0 }}</h2>
                <p class="mb-0">Quizzes</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card text-center bg-warning text-white">
              <div class="card-body">
                <h2>{{ stats.counts.attempts || 0 }}</h2>
                <p class="mb-0">Quiz Attempts</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card shadow mb-4">
      <div class="card-header">
        <h5 class="mb-0">Performance by Subject</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="!stats.subject_scores || stats.subject_scores.length === 0" class="text-center py-4">
          <p class="text-muted">No subject performance data available</p>
        </div>
        
        <div v-else>
          <canvas ref="statsChart" height="300"></canvas>
        </div>
      </div>
    </div>
    
    <div class="card shadow mb-4">
      <div class="card-header">
        <h5 class="mb-0">Recent Activity</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="!stats.recent_activity || stats.recent_activity.length === 0" class="text-center py-4">
          <p class="text-muted">No recent activity data available</p>
        </div>
        
        <div v-else>
          <ul class="list-group">
            <li v-for="activity in stats.recent_activity" :key="activity.id" class="list-group-item">
              <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                  <i :class="[getActivityIcon(activity.type), getActivityClass(activity.type), 'fa-lg me-3']"></i>
                </div>
                <div class="flex-grow-1">
                  <div class="d-flex justify-content-between">
                    <strong>{{ activity.user }}</strong>
                    <small>{{ formatDate(activity.timestamp) }}</small>
                  </div>
                  <div>{{ activity.action }}: {{ activity.details }}</div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="card shadow">
      <div class="card-header">
        <h5 class="mb-0">Quiz Distribution</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="!stats.quiz_distribution || stats.quiz_distribution.length === 0" class="text-center py-4">
          <p class="text-muted">No quiz distribution data available</p>
        </div>
        
        <div v-else>
          <canvas ref="quizDistChart" height="300"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'AdminStatistics',
  data() {
    return {
      stats: {
        counts: {},
        subject_scores: [],
        recent_activity: [],
        user_growth: {},
        quiz_distribution: []
      },
      loading: true,
      error: null,
      charts: {
        statsChart: null,
        quizDistChart: null
      },
      chartJsLoaded: false
    };
  },
  mounted() {
    this.initializeChartJs();
  },
  methods: {
    initializeChartJs() {
      // Check if Chart.js is loaded
      if (typeof window.Chart === 'undefined') {
        console.log('Chart.js not loaded yet, waiting...');
        // Wait for Chart.js to load
        const checkInterval = setInterval(() => {
          if (typeof window.Chart !== 'undefined') {
            console.log('Chart.js loaded successfully');
            clearInterval(checkInterval);
            this.chartJsLoaded = true;
            this.fetchStatistics();
          }
        }, 100);

        // Set a timeout to prevent infinite waiting
        setTimeout(() => {
          if (!this.chartJsLoaded) {
            clearInterval(checkInterval);
            this.error = 'Failed to load Chart.js library. Please refresh the page.';
            console.error('Chart.js failed to load after timeout');
          }
        }, 5000);
      } else {
        console.log('Chart.js already loaded');
        this.chartJsLoaded = true;
        this.fetchStatistics();
      }
    },
    async fetchStatistics() {
      this.loading = true;
      this.error = null;
      
      try {
        // Get the JWT token from local storage
        const token = localStorage.getItem('token');
        
        if (!token) {
          this.error = 'Authentication required. Please log in.';
          this.loading = false;
          return;
        }
        
        console.log('Fetching statistics data...');
        // Use the configured endpoint
        const endpoint = API_CONFIG.ENDPOINTS.ADMIN_STATS;
        console.log('Using statistics endpoint:', endpoint);
        console.log('Base URL:', API_CONFIG.BASE_URL);
        
        const response = await apiService.get(endpoint);
        console.log('Statistics API response:', response);
        
        // Check if response has the expected data
        if (response) {
          this.stats = response;
          
          // First mark loading as complete so template renders
          this.loading = false;
          
          // Wait for DOM to update, then render charts with a delay
          setTimeout(() => {
            this.renderCharts();
          }, 500);
        } else {
          console.error('Unexpected API response format:', response);
          this.error = 'Received invalid data format from server';
          this.loading = false;
        }
      } catch (err) {
        console.error('Error fetching statistics:', err);
        this.error = err.message || 'Failed to load statistics';
        this.loading = false;
      }
    },
    
    renderCharts() {
      console.log('Attempting to render charts...');
      // Make sure the chart instances are destroyed if they already exist
      if (this.charts.statsChart) {
        this.charts.statsChart.destroy();
        this.charts.statsChart = null;
      }
      
      if (this.charts.quizDistChart) {
        this.charts.quizDistChart.destroy();
        this.charts.quizDistChart = null;
      }
      
      // Render charts with a small delay between them
      this.renderSubjectChart();
      
      setTimeout(() => {
        this.renderQuizDistributionChart();
      }, 200);
    },
    
    renderSubjectChart() {
      if (!this.chartJsLoaded) {
        console.error('Chart.js not loaded yet');
        return;
      }

      if (!this.stats.subject_scores || this.stats.subject_scores.length === 0) {
        console.log('No subject scores data available for chart');
        return;
      }
      
      try {
        // Make sure the chart element exists in the DOM
        const chartElement = this.$refs.statsChart;
        if (!chartElement) {
          console.error('Chart canvas element not found');
          // Try again after a delay
          setTimeout(() => this.renderSubjectChart(), 300);
          return;
        }
        
        console.log('Found statsChart canvas element, initializing chart...');
        
        // Prepare data
        const labels = this.stats.subject_scores.map(subject => subject.name);
        const scores = this.stats.subject_scores.map(subject => subject.avgScore);
        const attempts = this.stats.subject_scores.map(subject => subject.attempts);
        
        // Create chart configuration
        const config = {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [
              {
                label: 'Average Score (%)',
                data: scores,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
              },
              {
                label: 'Attempts',
                data: attempts,
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                yAxisID: 'y-attempts'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            font: {
              family: "'Lexend', sans-serif"
            },
            plugins: {
              legend: {
                labels: {
                  font: {
                    family: "'Lexend', sans-serif",
                    size: 12
                  }
                }
              },
              title: {
                font: {
                  family: "'Lexend', sans-serif",
                  size: 16,
                  weight: 'bold'
                }
              },
              tooltip: {
                titleFont: {
                  family: "'Lexend', sans-serif"
                },
                bodyFont: {
                  family: "'Lexend', sans-serif"
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Average Score (%)',
                  font: {
                    family: "'Lexend', sans-serif",
                    weight: 'medium'
                  }
                },
                max: 100,
                ticks: {
                  font: {
                    family: "'Lexend', sans-serif"
                  }
                }
              },
              'y-attempts': {
                position: 'right',
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Attempts',
                  font: {
                    family: "'Lexend', sans-serif",
                    weight: 'medium'
                  }
                },
                grid: {
                  display: false
                },
                ticks: {
                  font: {
                    family: "'Lexend', sans-serif"
                  }
                }
              },
              x: {
                ticks: {
                  font: {
                    family: "'Lexend', sans-serif"
                  }
                }
              }
            }
          }
        };
        
        try {
          // Destroy previous chart instance if it exists
          if (this.charts.statsChart) {
            this.charts.statsChart.destroy();
          }
          
          // Create chart using the global Chart object
          this.charts.statsChart = new window.Chart(chartElement, config);
          console.log('Subject chart created successfully');
        } catch (chartError) {
          console.error('Error creating chart instance:', chartError);
          this.error = 'Failed to create chart. Please try refreshing the page.';
        }
      } catch (error) {
        console.error('Error rendering subject chart:', error);
        this.error = 'Error rendering chart. Please try refreshing the page.';
      }
    },
    
    renderQuizDistributionChart() {
      if (!this.chartJsLoaded) {
        console.error('Chart.js not loaded yet');
        return;
      }

      if (!this.stats.quiz_distribution || this.stats.quiz_distribution.length === 0) {
        console.log('No quiz distribution data available for chart');
        return;
      }
      
      try {
        // Make sure the chart element exists in the DOM
        const chartElement = this.$refs.quizDistChart;
        if (!chartElement) {
          console.error('Quiz distribution chart canvas element not found');
          // Try again after a delay
          setTimeout(() => this.renderQuizDistributionChart(), 300);
          return;
        }
        
        console.log('Found quizDistChart canvas element, initializing chart...');
        
        // Prepare data
        const labels = this.stats.quiz_distribution.map(item => item.subject);
        const data = this.stats.quiz_distribution.map(item => item.count);
        
        // Generate random colors
        const backgroundColors = labels.map(() => this.getRandomColor(0.5));
        const borderColors = labels.map(() => this.getRandomColor(1));
        
        // Chart configuration
        const config = {
          type: 'pie',
          data: {
            labels: labels,
            datasets: [
              {
                data: data,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            font: {
              family: "'Lexend', sans-serif"
            },
            plugins: {
              legend: {
                position: 'right',
                labels: {
                  font: {
                    family: "'Lexend', sans-serif",
                    size: 12
                  }
                }
              },
              title: {
                display: true,
                text: 'Quiz Distribution by Subject',
                font: {
                  family: "'Lexend', sans-serif",
                  size: 16,
                  weight: 'bold'
                }
              },
              tooltip: {
                titleFont: {
                  family: "'Lexend', sans-serif"
                },
                bodyFont: {
                  family: "'Lexend', sans-serif"
                }
              }
            }
          }
        };
        
        try {
          // Destroy previous chart instance if it exists
          if (this.charts.quizDistChart) {
            this.charts.quizDistChart.destroy();
          }
          
          // Create chart using the global Chart object
          this.charts.quizDistChart = new window.Chart(chartElement, config);
          console.log('Quiz distribution chart created successfully');
        } catch (chartError) {
          console.error('Error creating chart instance:', chartError);
          this.error = 'Failed to create chart. Please try refreshing the page.';
        }
      } catch (error) {
        console.error('Error rendering quiz distribution chart:', error);
        this.error = 'Error rendering chart. Please try refreshing the page.';
      }
    },
    
    getRandomColor(alpha = 1) {
      const r = Math.floor(Math.random() * 255);
      const g = Math.floor(Math.random() * 255);
      const b = Math.floor(Math.random() * 255);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      
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
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
          return dateString;
        }
        
        // Get time difference in minutes - using local time for comparison
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        
        // For very recent events - within the last minute
        if (diffSecs < 60) {
          return diffSecs <= 10 ? 'Just now' : `${diffSecs} seconds ago`;
        }
        
        // For events within the last hour
        const diffMins = Math.floor(diffSecs / 60);
        if (diffMins < 60) {
          return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        }
        
        // For events within the last day
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) {
          return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        }
        
        // If more than a day, show the actual date with time but NO timezone indication
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          timeZoneName: 'short',
          // Remove the timeZoneName to hide timezone
          timeZoneName: undefined
        });
      } catch (err) {
        console.error('Error formatting date:', err);
        return dateString;
      }
    },
    
    getActivityIcon(type) {
      switch (type) {
        case 'Quiz Completion':
          return 'fas fa-check-circle';
        case 'Registration':
          return 'fas fa-user-plus';
        case 'Content Update':
          return 'fas fa-edit';
        default:
          return 'fas fa-info-circle';
      }
    },
    
    getActivityClass(type) {
      switch (type) {
        case 'Quiz Completion':
          return 'text-success';
        case 'Registration':
          return 'text-primary';
        case 'Content Update':
          return 'text-info';
        default:
          return 'text-secondary';
      }
    },
    
    refreshStatistics() {
      console.log('Refreshing statistics data...');
      
      // Reset error state
      this.error = null;
      
      // Destroy existing charts
      if (this.charts.statsChart) {
        this.charts.statsChart.destroy();
        this.charts.statsChart = null;
      }
      
      if (this.charts.quizDistChart) {
        this.charts.quizDistChart.destroy();
        this.charts.quizDistChart = null;
      }
      
      // Fetch fresh data
      this.fetchStatistics();
    }
  }
};
</script>

<style scoped>
.admin-statistics {
  padding: 20px;
  font-family: 'Lexend', sans-serif;
}

.card {
  margin-bottom: 20px;
}

.card-header h5 {
  font-weight: 600;
}

.list-group-item {
  transition: background-color 0.2s;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

/* Custom styling for the summary cards */
.card h2 {
  font-weight: 700;
  font-size: 2.2rem;
  margin-bottom: 0.5rem;
}

.card p.mb-0 {
  font-weight: 500;
}
</style> 