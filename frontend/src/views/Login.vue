<template>
  <div class="login">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Login</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" v-model.trim="username" required>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" v-model.trim="password" required>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Login
                </button>
              </div>
            </form>
          </div>
          <div class="card-footer text-center">
            <p class="mb-0">Don't have an account? <router-link :to="{name: 'Register'}">Register</router-link></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import emitter from '@/utils/eventBus';
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;
      
      // Trim whitespace from inputs
      const username = this.username.trim();
      const password = this.password.trim();
      
      if (!username || !password) {
        this.error = 'Username and password are required';
        this.loading = false;
        return;
      }
      
      try {
        // Use the configured endpoint
        const response = await ApiService.post(API_CONFIG.ENDPOINTS.LOGIN, {
          username,
          password
        });
        
        // Validate response data
        if (!response || !response.access_token || !response.user) {
          throw new Error('Invalid response from server');
        }
        
        // Validate admin status if trying to access admin routes
        const isAdminRoute = this.$route.query.redirect?.includes('admin');
        if (isAdminRoute && !response.user.is_admin) {
          throw new Error('You do not have admin privileges');
        }
        
        // Store auth info in localStorage
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('token', response.access_token);
        
        // Notify about auth change
        emitter.emit('auth-changed');
        
        // Navigate to appropriate dashboard or redirect URL
        const redirectPath = this.$route.query.redirect || 
                           (response.user.is_admin ? 'AdminDashboard' : 'UserDashboard');
        this.$router.push({ name: redirectPath });
      } catch (error) {
        console.error('Login error:', error);
        this.error = error.message || 'Failed to login. Please check your credentials.';
        
        // Clear any invalid auth data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 