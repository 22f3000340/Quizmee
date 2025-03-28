<template>
  <div class="admin-dashboard">
    <h1 class="mb-4">Admin Dashboard</h1>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading dashboard data...</p>
    </div>
    
    <div v-else>
      <!-- Refresh Button -->
      <div class="d-flex justify-content-end mb-3">
        <button class="btn btn-primary" @click="refreshDashboard">
          <i class="fas fa-sync-alt me-1"></i> Refresh Dashboard
        </button>
      </div>
      
      <!-- No data message -->
      <div v-if="error" class="alert alert-danger">
        <strong>Error:</strong> {{ error }}
      </div>
      
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5 class="card-title">Users</h5>
              <h2 class="mb-0">{{ stats.counts.users }}</h2>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <span>Registered Users</span>
              <router-link :to="{name: 'AdminUsers'}" class="btn btn-light btn-sm">
                View
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="col-md-3 mb-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Subjects</h5>
              <h2 class="mb-0">{{ stats.counts.subjects }}</h2>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <span>Available Subjects</span>
              <router-link :to="{name: 'AdminSubjects'}" class="btn btn-light btn-sm">
                View
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="col-md-3 mb-3">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h5 class="card-title">Quizzes</h5>
              <h2 class="mb-0">{{ stats.counts.quizzes }}</h2>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <span>Total Quizzes</span>
              <router-link :to="{name: 'AdminSubjects'}" class="btn btn-light btn-sm">
                View
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="col-md-3 mb-3">
          <div class="card bg-warning text-dark">
            <div class="card-body">
              <h5 class="card-title">Quiz Attempts</h5>
              <h2 class="mb-0">{{ stats.counts.attempts }}</h2>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <span>Total Attempts</span>
              <router-link :to="{name: 'AdminStatistics'}" class="btn btn-light btn-sm">
                View
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0">Recent Activity</h5>
            </div>
            <div class="card-body">
              <div v-if="stats.recent_activity.length === 0" class="text-center py-4">
                <p class="text-muted">No data available</p>
              </div>
              <div v-else>
                <div class="list-group">
                  <div v-for="activity in visibleActivities" :key="activity.id" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                      <h6 class="mb-1">{{ activity.user }} {{ activity.action }}</h6>
                      <small>{{ formatDate(activity.timestamp) }}</small>
                    </div>
                    <p class="mb-1">{{ activity.details }}</p>
                    <small :class="getActivityClass(activity.type)">
                      <i :class="getActivityIcon(activity.type)"></i> {{ activity.type }}
                    </small>
                  </div>
                </div>
                
                <div v-if="stats.recent_activity.length > visibleActivitiesCount" class="text-center mt-3">
                  <button class="btn btn-outline-primary btn-sm" @click="loadMoreActivities">
                    <i class="fas fa-sync-alt me-1"></i> Load More
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0">Subject Performance</h5>
            </div>
            <div class="card-body">
              <div v-if="stats.subject_scores.length === 0" class="text-center py-4">
                <p class="text-muted">No data available</p>
              </div>
              <div v-else>
                <!-- Chart will go here -->
                <div id="subjectPerformanceChart" style="position: relative; height: 300px; width: 100%; margin-bottom: 15px;">
                  <!-- Chart will be rendered here -->
                </div>
                <!-- Progress bars for each subject -->
                <div v-for="subject in stats.subject_scores" :key="subject.id" class="mb-3">
                  <div class="d-flex justify-content-between">
                    <span>{{ subject.name }}</span>
                    <span>{{ subject.avgScore }}% ({{ subject.attempts }} attempts)</span>
                  </div>
                  <div class="progress" style="height: 15px;">
                    <div class="progress-bar" role="progressbar" 
                         :style="{ width: subject.avgScore + '%', backgroundColor: getScoreColor(subject.avgScore) }" 
                         :aria-valuenow="subject.avgScore" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 mb-4">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0">User Growth</h5>
            </div>
            <div class="card-body">
              <div class="text-center mb-3">
                <h2 :class="stats.user_growth.percentage >= 0 ? 'text-success' : 'text-danger'">
                  <i :class="stats.user_growth.percentage >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i> 
                  {{ Math.abs(stats.user_growth.percentage) }}%
                </h2>
                <small>Since last month</small>
              </div>
              
              <div class="row mb-3">
                <div class="col-6">
                  <div class="card bg-light">
                    <div class="card-body p-2">
                      <h6 class="text-muted">Total Users</h6>
                      <div class="d-flex justify-content-between">
                        <div>
                          <small class="text-muted">Last Month</small>
                          <div>{{ stats.user_growth.last_month_total || 0 }}</div>
                        </div>
                        <div>
                          <small class="text-muted">Now</small>
                          <div>{{ stats.user_growth.current_month_total || 0 }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="card bg-light">
                    <div class="card-body p-2">
                      <h6 class="text-muted">New Registrations</h6>
                      <div class="d-flex justify-content-between">
                        <div>
                          <small class="text-muted">Last Month</small>
                          <div>{{ stats.user_growth.last_month_new || 0 }}</div>
                        </div>
                        <div>
                          <small class="text-muted">This Month</small>
                          <div>{{ stats.user_growth.current_month_new || 0 }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="card bg-primary text-white">
                <div class="card-body p-2 text-center">
                  <h6 class="mb-1">Projected Next Month</h6>
                  <div class="d-flex justify-content-around">
                    <div>
                      <small>New Users</small>
                      <div class="h5 mb-0">{{ stats.user_growth.projected_new || 0 }}</div>
                    </div>
                    <div>
                      <small>Total Users</small>
                      <div class="h5 mb-0">{{ stats.user_growth.projected_total || 0 }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card shadow mt-4">
            <div class="card-header">
              <h5 class="mb-0">Quiz Distribution</h5>
            </div>
            <div class="card-body">
              <div v-if="stats.quiz_distribution.length === 0" class="text-center py-4">
                <p class="text-muted">No data available</p>
              </div>
              <div v-else>
                <!-- Pie chart container -->
                <div id="quizDistributionChart" style="position: relative; height: 200px; width: 100%; margin-bottom: 15px; z-index: 10;">
                  <!-- Pie chart will be rendered here -->
                </div>
                
                <div v-for="item in stats.quiz_distribution" :key="item.subject" class="mb-2">
                  <div class="d-flex justify-content-between align-items-center">
                    <span>{{ item.subject }}</span>
                    <span class="badge bg-primary">{{ item.count }}</span>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-primary" role="progressbar" 
                         :style="{ width: (item.count / stats.counts.quizzes * 100) + '%' }" 
                         :aria-valuenow="item.count" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                </div>
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
  name: 'AdminDashboard',
  data() {
    return {
      stats: {
        counts: {
          users: 0,
          subjects: 0,
          quizzes: 0,
          attempts: 0
        },
        subject_scores: [],
        recent_activity: [],
        user_growth: {
          percentage: 0,
          last_month: 0,
          current_month: 0,
          projected: 0
        },
        quiz_distribution: []
      },
      loading: true,
      error: null,
      subjectChart: null,
      quizPieChart: null,
      visibleActivities: [],
      visibleActivitiesCount: 6
    }
  },
  mounted() {
    this.fetchDashboardData();
    
    // Add a script tag to ensure Chart.js is loaded properly (if not already present)
    const chartScriptId = 'chartjs-script';
    if (!document.getElementById(chartScriptId) && typeof Chart === 'undefined') {
      console.log('Loading Chart.js dynamically');
      const script = document.createElement('script');
      script.id = chartScriptId;
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js';
      script.integrity = 'sha256-Y26AMvaIfrZ1EQU49pf6H4QzVTrOI8m9wQYKkftBt4s=';
      script.crossOrigin = 'anonymous';
      script.onload = () => {
        console.log('Chart.js loaded dynamically for admin dashboard');
        // Wait a moment before rendering charts to ensure DOM is ready
        setTimeout(() => {
          if (this.stats.subject_scores.length > 0) {
            console.log('Rendering subject chart after Chart.js load');
            this.renderSubjectChart();
          }
          if (this.stats.quiz_distribution.length > 0) {
            console.log('Rendering quiz distribution pie chart after Chart.js load');
            this.renderQuizPieChart();
          }
        }, 300);
      };
      document.head.appendChild(script);
    } else {
      console.log('Chart.js already available');
    }
  },
  methods: {
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;
      try {
        // Debug JWT token and user info
        const token = localStorage.getItem('token');
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        console.log('JWT Token:', token ? token.substring(0, 20) + '...' : 'No token');
        console.log('User info:', user);
        console.log('Is admin:', user.is_admin);
        
        let response = null;
        
        const endpointPatterns = [
          API_CONFIG.ENDPOINTS.ADMIN_STATS, // Primary endpoint from config
          '/admin/statistics',              // Alternative endpoint pattern
          '/api/admin/statistics',          // Another common pattern
          '/admin/stats'                    // Short form
        ];
        
        // Try each endpoint pattern until we get a response
        for (const endpoint of endpointPatterns) {
          try {
            console.log(`Trying to fetch admin statistics from: ${endpoint}`);
            response = await ApiService.get(endpoint);
            console.log(`Response from ${endpoint}:`, response);
            
            // Check if the response is empty, null, or just an empty object
            if (response && Object.keys(response).length > 0) {
              console.log(`Successfully fetched non-empty data from ${endpoint}`);
              break; // Exit the loop if we get a valid response
            } else {
              console.log(`Endpoint ${endpoint} returned empty data`);
            }
          } catch (err) {
            console.log(`Endpoint ${endpoint} failed:`, err.message);
            // Continue to the next endpoint
          }
        }
        
        if (!response || Object.keys(response).length === 0) {
          throw new Error('Failed to fetch dashboard data from any endpoint');
        }
        
        this.processResponse(response);
      } catch (error) {
        console.error('Error in fetchDashboardData:', error);
        this.loading = false;
        this.error = error.message || 'Failed to load dashboard data';
      }
    },
    
    processResponse(response) {
      // Log raw response for debugging
      console.log('Raw API response:', response);
      
      // Set default values if response is null
      if (!response) {
        this.stats = this.getDefaultStats();
        return;
      }
      
      // Check if the response has a data field (API wrapped format)
      const data = response.data || response;
      
      // Attempt to extract the counts with various possible field names
      const userCount = data.user_count || data.users_count || 
                        (data.counts && data.counts.users) || 0;
      
      const subjectCount = data.subject_count || data.subjects_count || 
                          (data.counts && data.counts.subjects) || 0;
      
      const quizCount = data.quiz_count || data.quizzes_count || 
                        (data.counts && data.counts.quizzes) || 0;
      
      const attemptCount = data.attempt_count || data.attempts_count || 
                          (data.counts && data.counts.attempts) || 0;
      
      // Process subject scores with field name flexibility
      let subjectScores = data.subject_scores || data.subject_performance || 
                         data.subjects || [];
      
      // Map subject scores to expected format if needed
      if (subjectScores.length > 0) {
        // Check if we need to transform the data
        if (typeof subjectScores[0].avgScore === 'undefined') {
          subjectScores = subjectScores.map(subject => ({
            id: subject.id || subject.subject_id,
            name: subject.name || subject.subject_name,
            avgScore: subject.avg_score || subject.average_score || subject.score || 0,
            attempts: subject.attempts || subject.attempt_count || 0
          }));
        }
      }
      
      // Get recent activities
      const recentActivities = data.recent_activity || data.activities || [];
      
      // Process API response
      this.stats = {
        counts: {
          users: userCount,
          subjects: subjectCount,
          quizzes: quizCount,
          attempts: attemptCount
        },
        subject_scores: subjectScores,
        recent_activity: recentActivities,
        user_growth: this.extractUserGrowth(data),
        quiz_distribution: data.quiz_distribution || data.quizzes_by_subject || []
      };
      
      // Initialize visible activities (first 6)
      this.visibleActivitiesCount = 6;
      this.updateVisibleActivities();
      
      console.log('Processed stats:', this.stats);
      
      this.loading = false;
      
      // Render the charts after loading data
      setTimeout(() => {
        this.renderSubjectChart();
        this.renderQuizPieChart();
      }, 300);
    },
    
    getDefaultStats() {
      return {
        counts: {
          users: 0,
          subjects: 0,
          quizzes: 0,
          attempts: 0
        },
        subject_scores: [],
        recent_activity: [],
        user_growth: {
          percentage: 0,
          last_month_new: 0,
          current_month_new: 0,
          last_month_total: 0,
          current_month_total: 0,
          projected_new: 0,
          projected_total: 0
        },
        quiz_distribution: []
      };
    },
    
    extractUserGrowth(data) {
      // Handle different possible formats for user growth data
      if (data.user_growth && typeof data.user_growth === 'object') {
        // Check if it's the new format with detailed metrics
        if ('last_month_new' in data.user_growth) {
          return {
            percentage: data.user_growth.percentage || 0,
            last_month_new: data.user_growth.last_month_new || 0,
            current_month_new: data.user_growth.current_month_new || 0,
            last_month_total: data.user_growth.last_month_total || 0,
            current_month_total: data.user_growth.current_month_total || 0,
            projected_new: data.user_growth.projected_new || 0,
            projected_total: data.user_growth.projected_total || 0
          };
        }
        
        // Legacy format compatibility
        return {
          percentage: data.user_growth.percentage || 0,
          last_month_new: 0,
          current_month_new: 0,
          last_month_total: data.user_growth.last_month || 0,
          current_month_total: data.user_growth.current_month || 0,
          projected_new: Math.round((data.user_growth.projected || 0) * 0.1), // Estimate
          projected_total: data.user_growth.projected || 0
        };
      } else if (data.growth && typeof data.growth === 'object') {
        // Alternative format
        return {
          percentage: data.growth.percentage || 0,
          last_month_new: data.growth.last_month_new || 0,
          current_month_new: data.growth.current_month_new || 0,
          last_month_total: data.growth.last_month_total || data.growth.last_month || 0,
          current_month_total: data.growth.current_month_total || data.growth.current_month || 0,
          projected_new: data.growth.projected_new || 0,
          projected_total: data.growth.projected_total || data.growth.projected || 0
        };
      } else {
        // If no structured growth data, return default empty structure
        return {
          percentage: data.growth_percentage || 0,
          last_month_new: 0,
          current_month_new: 0,
          last_month_total: data.last_month_users || 0,
          current_month_total: data.current_month_users || 0,
          projected_new: 0,
          projected_total: data.projected_users || 0
        };
      }
    },
    
    formatDate(date) {
      if (!date) return '';
      
      // Convert to Date object if it's a string
      // Note: ISO string dates from API are in UTC, adjust for timezone differences
      const now = new Date();
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
      
      // Get time difference in seconds
      const diffMs = now - dateObj;
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
      
      // For older dates, show the full date with time but no timezone
      return dateObj.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    getScoreColor(score) {
      if (score >= 80) return '#28a745'; // Success
      if (score >= 60) return '#17a2b8'; // Info
      if (score >= 40) return '#ffc107'; // Warning
      return '#dc3545'; // Danger
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
    
    renderSubjectChart() {
      // Skip if no data or Chart is not available
      if (this.stats.subject_scores.length === 0) return;
      if (typeof Chart === 'undefined') {
        console.log('Chart.js not available yet, waiting...');
        return;
      }
      
      // Get container element
      const container = document.getElementById('subjectPerformanceChart');
      if (!container) {
        console.error('Chart container not found');
        return;
      }
      
      // Destroy existing chart if it exists
      if (this.subjectChart) {
        this.subjectChart.destroy();
        this.subjectChart = null;
      }
      
      // Clear any existing content
      container.innerHTML = '';
      
      try {
        // Create canvas element
        const canvas = document.createElement('canvas');
        canvas.id = 'subject-chart';
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
        
        // Prepare data
        const labels = this.stats.subject_scores.map(s => s.name);
        const avgScores = this.stats.subject_scores.map(s => s.avgScore);
        const attempts = this.stats.subject_scores.map(s => s.attempts);
        
        // Color array for each bar
        const colors = this.stats.subject_scores.map(s => this.getScoreColor(s.avgScore));
        
        console.log('Rendering chart with data:', {labels, avgScores, attempts});
        
        // Create chart - using bar chart
        this.subjectChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [
              {
                label: 'Average Score (%)',
                data: avgScores,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.2', '1')),
                borderWidth: 1,
                yAxisID: 'y'
              },
              {
                label: 'Number of Attempts',
                data: attempts,
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1,
                type: 'line',
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                type: 'linear',
                position: 'left',
                min: 0,
                max: 100,
                title: {
                  display: true,
                  text: 'Average Score (%)'
                }
              },
              y1: {
                type: 'linear',
                position: 'right',
                min: 0,
                grid: {
                  drawOnChartArea: false
                },
                title: {
                  display: true,
                  text: 'Number of Attempts'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Subjects'
                }
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(context) {
                    if (context.dataset.label === 'Average Score (%)') {
                      return `Average Score: ${context.formattedValue}%`;
                    } else {
                      return `Attempts: ${context.formattedValue}`;
                    }
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
        
        console.log('Subject chart rendered successfully');
      } catch (error) {
        console.error('Error rendering subject chart:', error);
        // Fallback to standard display if chart fails
        container.innerHTML = '<p class="text-center text-muted">Chart could not be rendered</p>';
      }
    },
    
    renderQuizPieChart() {
      console.log('renderQuizPieChart called');
      console.log('Quiz distribution data:', this.stats.quiz_distribution);
      
      // Skip if no data or Chart is not available
      if (this.stats.quiz_distribution.length === 0) {
        console.log('No quiz distribution data available, skipping chart');
        return;
      }
      
      if (typeof Chart === 'undefined') {
        console.log('Chart.js not available yet for quiz pie chart, waiting...');
        this.loadChartJsManually(() => this.renderQuizPieChart());
        return;
      }
      
      // Get container element
      const container = document.getElementById('quizDistributionChart');
      if (!container) {
        console.error('Quiz pie chart container not found');
        console.log('Looking for element with ID:', 'quizDistributionChart');
        // Try to find the container by querying all elements
        const allDivs = document.querySelectorAll('div');
        console.log('Total divs on page:', allDivs.length);
        return;
      }
      
      console.log('Quiz pie chart container found, dimensions:', container.offsetWidth, 'x', container.offsetHeight);
      
      // Destroy existing chart if it exists
      if (this.quizPieChart) {
        console.log('Destroying existing pie chart instance');
        this.quizPieChart.destroy();
        this.quizPieChart = null;
      }
      
      // Clear any existing content
      container.innerHTML = '';
      
      try {
        // Create canvas element
        console.log('Creating canvas for pie chart');
        const canvas = document.createElement('canvas');
        canvas.id = 'quiz-pie-chart';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        
        // Add to container
        container.appendChild(canvas);
        
        // Handle DPI scaling for canvas
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        
        console.log('Canvas dimensions:', canvas.width, 'x', canvas.height, '(DPI:', dpr, ')');
        
        // Get the 2D context
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
        
        // Prepare data
        const labels = this.stats.quiz_distribution.map(item => item.subject);
        const data = this.stats.quiz_distribution.map(item => item.count);
        
        console.log('Pie chart data prepared:', { labels, data });
        
        // Generate a vibrant color palette for the pie chart
        const backgroundColors = [
          'rgba(255, 99, 132, 0.8)',   // Red
          'rgba(54, 162, 235, 0.8)',   // Blue
          'rgba(255, 206, 86, 0.8)',   // Yellow
          'rgba(75, 192, 192, 0.8)',   // Green
          'rgba(153, 102, 255, 0.8)',  // Purple
          'rgba(255, 159, 64, 0.8)',   // Orange
          'rgba(199, 199, 199, 0.8)',  // Gray
          'rgba(83, 102, 255, 0.8)',   // Indigo
          'rgba(255, 99, 255, 0.8)',   // Pink
          'rgba(20, 159, 164, 0.8)'    // Teal
        ];
        
        // Ensure we have enough colors by repeating if necessary
        const colors = this.stats.quiz_distribution.map((_, index) => 
          backgroundColors[index % backgroundColors.length]
        );
        
        console.log('Creating Chart.js pie chart instance');
        
        // Create pie chart
        this.quizPieChart = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: labels,
            datasets: [{
              data: data,
              backgroundColor: colors,
              borderColor: colors.map(color => color.replace('0.8', '1')),
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: {
                  boxWidth: 15,
                  padding: 10,
                  font: {
                    size: 11
                  }
                }
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || '';
                    const value = context.formattedValue || '';
                    const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                    const percentage = Math.round((context.raw / total) * 100);
                    return `${label}: ${value} (${percentage}%)`;
                  }
                }
              }
            }
          }
        });
        
        console.log('Quiz pie chart rendered successfully');
      } catch (error) {
        console.error('Error rendering quiz pie chart:', error);
        // Fallback to standard display if chart fails
        container.innerHTML = '<p class="text-center text-muted">Pie chart could not be rendered</p>';
      }
    },
    
    loadChartJsManually(callback) {
      console.log('Manually loading Chart.js');
      // Check if already loading
      if (document.getElementById('chartjs-script')) {
        console.log('Chart.js is already loading, waiting...');
        setTimeout(() => {
          if (typeof Chart !== 'undefined') {
            console.log('Chart.js now available, executing callback');
            callback();
          } else {
            console.log('Chart.js still not available, waiting longer...');
            setTimeout(callback, 1000);
          }
        }, 500);
        return;
      }
      
      // Add script tag
      const script = document.createElement('script');
      script.id = 'chartjs-script';
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js';
      script.integrity = 'sha256-Y26AMvaIfrZ1EQU49pf6H4QzVTrOI8m9wQYKkftBt4s=';
      script.crossOrigin = 'anonymous';
      script.onload = () => {
        console.log('Chart.js loaded dynamically via manual loading');
        callback();
      };
      document.head.appendChild(script);
    },
    
    refreshDashboard() {
      console.log('Refreshing dashboard data...');
      
      // Reset all state first
      this.error = null;
      this.loading = true;
      
      // Reset visible activities count
      this.visibleActivitiesCount = 6;
      
      // Clear existing charts to force redraw
      if (this.subjectChart) {
        this.subjectChart.destroy();
        this.subjectChart = null;
      }
      
      if (this.quizPieChart) {
        this.quizPieChart.destroy();
        this.quizPieChart = null;
      }
      
      // Fetch fresh data
      this.fetchDashboardData()
        .then(() => {
          console.log('Dashboard data refreshed successfully');
          
          // Force re-rendering charts after refresh
          setTimeout(() => {
            if (this.stats.subject_scores && this.stats.subject_scores.length > 0) {
              this.renderSubjectChart();
            }
            
            if (this.stats.quiz_distribution && this.stats.quiz_distribution.length > 0) {
              this.renderQuizPieChart();
            }
          }, 500);
        })
        .catch(error => {
          console.error('Error refreshing dashboard:', error);
        });
    },
    
    loadMoreActivities() {
      this.visibleActivitiesCount += 6;
      this.updateVisibleActivities();
    },
    
    updateVisibleActivities() {
      this.visibleActivities = this.stats.recent_activity.slice(0, this.visibleActivitiesCount);
    }
  }
}
</script>

<style scoped>
.progress {
  background-color: #f5f5f5;
}
.list-group-item-action:hover {
  background-color: #f8f9fa;
}

/* Chart container styles */
#subjectPerformanceChart, #quizDistributionChart {
  position: relative;
  min-height: 200px;
  z-index: 10;
  background: #fff;
  border-radius: 4px;
  overflow: visible !important;
}

/* Ensure chart canvas is visible */
canvas {
  max-width: 100%;
  position: relative;
  z-index: 20;
}
</style> 