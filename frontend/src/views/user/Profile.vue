<template>
  <div class="user-profile">
    <div class="container py-4">
      <h1 class="mb-4">My Profile</h1>
      
      <div v-if="error" class="alert alert-danger" role="alert">
        <i class="fas fa-exclamation-triangle me-2"></i> {{ error }}
      </div>
      
      <div v-if="successMessage" class="alert alert-success" role="alert">
        <i class="fas fa-check-circle me-2"></i> {{ successMessage }}
      </div>
      
      <!-- Loading state -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">Loading profile...</p>
      </div>
      
      <div v-else class="row">
        <!-- Profile Info Card -->
        <div class="col-md-4 mb-4">
          <div class="card shadow">
            <div class="card-body text-center">
              <div class="avatar-circle bg-primary text-white d-inline-flex align-items-center justify-content-center rounded-circle mb-3" style="width: 100px; height: 100px; font-size: 2.5rem;">
                {{ profile.username ? profile.username.charAt(0).toUpperCase() : '?' }}
              </div>
              <h3 class="mb-1">{{ profile.full_name }}</h3>
              <p class="text-muted mb-2">{{ profile.username }}</p>
              <p class="mb-3">
                <span class="badge bg-info">{{ profile.is_admin ? 'Administrator' : 'Student' }}</span>
              </p>
              <button class="btn btn-primary" @click="toggleEditMode">
                <i class="fas fa-edit me-1"></i> {{ editMode ? 'Cancel Edit' : 'Edit Profile' }}
              </button>
            </div>
            <div class="card-footer bg-light">
              <div class="d-flex align-items-center">
                <i class="fas fa-envelope text-muted me-2"></i>
                <span>{{ profile.email }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Profile Details/Edit Form -->
        <div class="col-md-8">
          <div class="card shadow">
            <div class="card-header bg-light">
              <h5 class="mb-0">{{ editMode ? 'Edit Profile Information' : 'Profile Information' }}</h5>
            </div>
            <div class="card-body">
              <!-- View Mode -->
              <div v-if="!editMode">
                <div class="row mb-3">
                  <div class="col-md-4 text-muted">Full Name:</div>
                  <div class="col-md-8 fw-semi-bold">{{ profile.full_name }}</div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-4 text-muted">Username:</div>
                  <div class="col-md-8">{{ profile.username }}</div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-4 text-muted">Email:</div>
                  <div class="col-md-8">{{ profile.email }}</div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-4 text-muted">Qualification:</div>
                  <div class="col-md-8">{{ profile.qualification || 'Not specified' }}</div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-4 text-muted">Date of Birth:</div>
                  <div class="col-md-8">{{ formatDate(profile.date_of_birth) || 'Not specified' }}</div>
                </div>
              </div>
              
              <!-- Edit Mode -->
              <form v-else @submit.prevent="updateProfile">
                <div class="mb-3">
                  <label for="fullName" class="form-label">Full Name</label>
                  <input type="text" class="form-control" id="fullName" v-model="editedProfile.full_name" required>
                </div>
                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input type="email" class="form-control" id="email" v-model="editedProfile.email" required>
                </div>
                <div class="mb-3">
                  <label for="qualification" class="form-label">Qualification</label>
                  <input type="text" class="form-control" id="qualification" v-model="editedProfile.qualification">
                </div>
                <div class="mb-3">
                  <label for="dob" class="form-label">Date of Birth</label>
                  <input type="date" class="form-control" id="dob" v-model="editedProfile.date_of_birth">
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">New Password (leave blank to keep current)</label>
                  <input type="password" class="form-control" id="password" v-model="editedProfile.password" autocomplete="new-password">
                </div>
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm New Password</label>
                  <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" autocomplete="new-password">
                </div>
                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                  <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
                  <button type="submit" class="btn btn-success" :disabled="saving">
                    <span v-if="saving">
                      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                      Saving...
                    </span>
                    <span v-else>
                      <i class="fas fa-save me-1"></i> Save Changes
                    </span>
                  </button>
                </div>
              </form>
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
import emitter from '@/utils/eventBus';

export default {
  name: 'UserProfile',
  data() {
    return {
      loading: true,
      saving: false,
      error: null,
      successMessage: null,
      profile: {},
      editMode: false,
      editedProfile: {
        full_name: '',
        email: '',
        qualification: '',
        date_of_birth: '',
        password: ''
      },
      confirmPassword: ''
    };
  },
  mounted() {
    this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await ApiService.get(API_CONFIG.ENDPOINTS.USER_PROFILE);
        this.profile = response;
        this.resetEditForm();
      } catch (err) {
        console.error('Error fetching profile:', err);
        this.error = err.message || 'Failed to load profile';
      } finally {
        this.loading = false;
      }
    },
    
    toggleEditMode() {
      this.editMode = !this.editMode;
      if (this.editMode) {
        this.resetEditForm();
      }
    },
    
    resetEditForm() {
      // Reset form fields to current profile values
      this.editedProfile = {
        full_name: this.profile.full_name || '',
        email: this.profile.email || '',
        qualification: this.profile.qualification || '',
        date_of_birth: this.profile.date_of_birth || '',
        password: ''
      };
      this.confirmPassword = '';
      this.error = null;
      this.successMessage = null;
    },
    
    cancelEdit() {
      this.editMode = false;
      this.resetEditForm();
    },
    
    async updateProfile() {
      // Validate passwords if one is entered
      if (this.editedProfile.password && this.editedProfile.password !== this.confirmPassword) {
        this.error = 'Passwords do not match';
        return;
      }
      
      this.saving = true;
      this.error = null;
      this.successMessage = null;
      
      // Remove password field if empty
      const dataToSend = { ...this.editedProfile };
      if (!dataToSend.password) {
        delete dataToSend.password;
      }
      
      try {
        const response = await ApiService.put(API_CONFIG.ENDPOINTS.USER_PROFILE, dataToSend);
        
        // Update local profile with response data
        this.profile = response;
        
        // Update user data in local storage (to reflect name changes in navbar)
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        userData.full_name = response.full_name;
        userData.email = response.email;
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Notify other components about the user data change
        emitter.emit('auth-changed');
        
        this.successMessage = 'Profile updated successfully';
        this.editMode = false;
      } catch (err) {
        console.error('Error updating profile:', err);
        this.error = err.message || 'Failed to update profile';
      } finally {
        this.saving = false;
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        let date;
        
        if (typeof dateString === 'string') {
          // Handle various date string formats
          if (dateString.endsWith('Z') || dateString.includes('+')) {
            date = new Date(dateString);
          } else {
            date = new Date(dateString + 'T00:00:00Z');
          }
        } else {
          date = new Date(dateString);
        }
        
        // Format: January 1, 2023
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      } catch (err) {
        console.error('Error formatting date:', err);
        return dateString;
      }
    }
  }
};
</script>

<style scoped>
.fw-semi-bold {
  font-weight: 600;
}
</style> 