<template>
  <div class="register">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Register</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" v-model="formData.username" required>
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="formData.email" required>
              </div>
              <div class="mb-3">
                <label for="fullName" class="form-label">Full Name</label>
                <input type="text" class="form-control" id="fullName" v-model="formData.full_name" required>
              </div>
              <div class="mb-3">
                <label for="qualification" class="form-label">Qualification</label>
                <input type="text" class="form-control" id="qualification" v-model="formData.qualification">
              </div>
              <div class="mb-3">
                <label for="dob" class="form-label">Date of Birth</label>
                <input type="date" class="form-control" id="dob" v-model="formData.date_of_birth">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" v-model="formData.password" required>
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm Password</label>
                <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" required>
                <div class="form-text text-danger" v-if="passwordMismatch">
                  Passwords do not match
                </div>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="loading || passwordMismatch">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Register
                </button>
              </div>
            </form>
          </div>
          <div class="card-footer text-center">
            <p class="mb-0">Already have an account? <router-link :to="{name: 'Login'}">Login</router-link></p>
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
  name: 'RegisterView',
  data() {
    return {
      formData: {
        username: '',
        email: '',
        full_name: '',
        qualification: '',
        date_of_birth: '',
        password: ''
      },
      confirmPassword: '',
      loading: false,
      error: null,
      success: null
    }
  },
  computed: {
    passwordMismatch() {
      return this.formData.password && this.confirmPassword && 
             this.formData.password !== this.confirmPassword
    }
  },
  methods: {
    async handleRegister() {
      if (this.passwordMismatch) {
        return;
      }
      
      this.loading = true;
      this.error = null;
      this.success = null;
      
      // Basic validation
      if (!this.formData.username.trim()) {
        this.error = 'Username is required';
        this.loading = false;
        return;
      }
      
      if (!this.formData.email.trim() || !this.isValidEmail(this.formData.email)) {
        this.error = 'Please enter a valid email address';
        this.loading = false;
        return;
      }
      
      if (this.formData.password.length < 6) {
        this.error = 'Password must be at least 6 characters long';
        this.loading = false;
        return;
      }
      
      try {
        // Log the endpoint being used
        console.log('Attempting registration with endpoint:', API_CONFIG.ENDPOINTS.REGISTER);
        
        // Use the real backend
        const response = await ApiService.post(API_CONFIG.ENDPOINTS.REGISTER, {
          username: this.formData.username.trim(),
          email: this.formData.email.trim(),
          full_name: this.formData.full_name.trim(),
          qualification: this.formData.qualification.trim(),
          date_of_birth: this.formData.date_of_birth,
          password: this.formData.password.trim()
        });
        
        // Show success message
        this.success = response.message || 'Registration successful! You can now login.';
        
        // Reset form
        this.resetForm();
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          this.$router.push({ name: 'Login' });
        }, 2000);
      } catch (error) {
        console.error('Registration error:', error);
        this.error = error.message || 'Failed to register. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    resetForm() {
      this.formData = {
        username: '',
        email: '',
        full_name: '',
        qualification: '',
        date_of_birth: '',
        password: ''
      };
      this.confirmPassword = '';
    },
    
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }
  }
}
</script> 