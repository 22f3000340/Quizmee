<template>
  <div class="admin-users">
    <h1 class="mb-4">Manage Users</h1>
    
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <div class="card shadow">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading users...</p>
        </div>
        
        <div v-else-if="users.length === 0" class="text-center py-5">
          <p class="text-muted">No users found.</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Qualification</th>
                <th>Date of Birth</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in displayedUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.full_name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.qualification || '-' }}</td>
                <td>{{ formatDate(user.date_of_birth) }}</td>
                <td>
                  <button class="btn btn-sm btn-info me-1" title="View User Details" @click="viewUser(user)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-danger" title="Delete User" @click="confirmDeleteUser(user)">
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- View User Modal -->
    <div v-if="showViewModal && selectedUser" class="modal fade show" tabindex="-1" style="display: block;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Profile</h5>
            <button type="button" class="btn-close" @click="closeViewModal"></button>
          </div>
          <div class="modal-body">
            <div class="text-center mb-3">
              <div class="avatar-circle bg-primary text-white d-inline-flex align-items-center justify-content-center rounded-circle mb-2" style="width: 80px; height: 80px; font-size: 1.5rem;">
                {{ selectedUser.username ? selectedUser.username.charAt(0).toUpperCase() : '?' }}
              </div>
              <h4>{{ selectedUser.full_name || selectedUser.username }}</h4>
            </div>
            
            <div class="mb-2">
              <h6 class="text-muted">Username</h6>
              <p>{{ selectedUser.username }}</p>
            </div>
            
            <div class="mb-2">
              <h6 class="text-muted">Email</h6>
              <p>{{ selectedUser.email }}</p>
            </div>
            
            <div class="mb-2">
              <h6 class="text-muted">Qualification</h6>
              <p>{{ selectedUser.qualification || 'Not specified' }}</p>
            </div>
            
            <div class="mb-2">
              <h6 class="text-muted">Date of Birth</h6>
              <p>{{ formatDate(selectedUser.date_of_birth) || 'Not specified' }}</p>
            </div>
            
            <div class="mb-2">
              <h6 class="text-muted">Account Type</h6>
              <p>{{ selectedUser.is_admin ? 'Administrator' : 'Regular User' }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeViewModal">Close</button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal && selectedUser" class="modal fade show" tabindex="-1" style="display: block;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Deletion</h5>
            <button type="button" class="btn-close" @click="closeDeleteModal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete the user <strong>{{ selectedUser.username }}</strong>?</p>
            <p class="text-danger">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDeleteModal">Cancel</button>
            <button type="button" class="btn btn-danger" :disabled="loading" @click="deleteUser">
              <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Delete User
            </button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </div>
</template>

<script>
import apiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'AdminUsers',
  data() {
    return {
      users: [],
      loading: true,
      error: null,
      selectedUser: null,
      showViewModal: false,
      showDeleteModal: false
    };
  },
  mounted() {
    this.fetchUsers();
  },
  computed: {
    displayedUsers() {
      // Filter out admin users
      return this.users.filter(user => !user.is_admin);
    }
  },
  methods: {
    async fetchUsers() {
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
        
        console.log('Fetching users data...');
        const response = await apiService.get(API_CONFIG.ENDPOINTS.USERS);
        console.log('Users API response:', response);
        
        // Check if the response has the expected format
        if (response && response.users) {
          this.users = response.users;
        } else {
          console.error('Unexpected API response format:', response);
          this.error = 'Received invalid data format from server';
        }
      } catch (err) {
        console.error('Error fetching users:', err);
        this.error = err.message || 'Failed to load users';
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      // Handle ISO strings from API (which are in UTC time)
      try {
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
        
        // For DOB, we only want to show the date (no time)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      } catch (err) {
        console.error('Error formatting date:', err);
        return dateString;
      }
    },

    viewUser(user) {
      this.selectedUser = user;
      this.showViewModal = true;
    },

    confirmDeleteUser(user) {
      this.selectedUser = user;
      this.showDeleteModal = true;
    },
    
    async deleteUser() {
      if (!this.selectedUser) return;
      
      try {
        this.loading = true;
        await apiService.delete(`${API_CONFIG.ENDPOINTS.USERS}/${this.selectedUser.id}`);
        
        // Remove user from the list
        this.users = this.users.filter(user => user.id !== this.selectedUser.id);
        
        // Close modal and reset selected user
        this.showDeleteModal = false;
        this.selectedUser = null;
        
        // Show success message (you could add a toast notification here)
        alert('User deleted successfully');
      } catch (err) {
        console.error('Error deleting user:', err);
        this.error = err.message || 'Failed to delete user';
      } finally {
        this.loading = false;
      }
    },
    
    closeViewModal() {
      this.showViewModal = false;
      this.selectedUser = null;
    },
    
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.selectedUser = null;
    }
  }
};
</script>

<style scoped>
.admin-users {
  padding: 20px;
}

/* Modal Styles */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
  overflow-y: auto;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  z-index: -1;
  width: 100%;
  height: 100%;
}

.avatar-circle {
  font-weight: bold;
}
</style> 