<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <a class="navbar-brand" href="#">Quiz Master V2</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <!-- Authenticated User Navigation -->
        <template v-if="isAuthenticated">
          <ul class="navbar-nav me-auto">
            <!-- Admin Menu -->
            <template v-if="isAdmin">
              <li class="nav-item">
                <router-link class="nav-link" :to="{name: 'AdminDashboard'}">Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" :to="{name: 'AdminSubjects'}">Subjects</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" :to="{name: 'AdminUsers'}">Users</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" :to="{name: 'AdminStatistics'}">Statistics</router-link>
              </li>
            </template>
            <!-- User Menu -->
            <template v-else>
              <li class="nav-item">
                <router-link class="nav-link" :to="{name: 'UserDashboard'}">Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" :to="{name: 'UserSubjects'}">Subjects</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" :to="{name: 'UserScores'}">My Scores</router-link>
              </li>
            </template>
          </ul>
          <div class="d-flex align-items-center">
            <div class="dropdown">
              <button class="btn btn-outline-light dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="fas fa-user me-1"></i> {{ userName }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li>
                  <router-link class="dropdown-item" :to="{name: 'UserProfile'}">
                    <i class="fas fa-id-card me-1"></i> My Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <button class="dropdown-item" @click="logout">
                    <i class="fas fa-sign-out-alt me-1"></i> Logout
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </template>
        
        <!-- Guest Navigation -->
        <template v-else>
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" :to="{name: 'Home'}">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="{name: 'About'}" v-if="$router.hasRoute && $router.hasRoute('About')">About</router-link>
            </li>
          </ul>
          <div class="d-flex">
            <router-link :to="{name: 'Login'}" class="btn btn-outline-light me-2">
              <i class="fas fa-sign-in-alt me-1"></i> Login
            </router-link>
            <router-link :to="{name: 'Register'}" class="btn btn-light">
              <i class="fas fa-user-plus me-1"></i> Register
            </router-link>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>

<script>
import emitter from '@/utils/eventBus';

export default {
  name: 'MainNavbar',
  data() {
    return {
      localAuth: !!localStorage.getItem('token'),
      localUser: this.getUserData()
    };
  },
  created() {
    // Listen for auth events
    emitter.on('auth-changed', this.checkAuthStatus);
    
    // Also listen for localStorage changes (for multi-tab support)
    window.addEventListener('storage', this.handleStorageChange);
  },
  beforeUnmount() {
    // Clean up event listeners
    emitter.off('auth-changed', this.checkAuthStatus);
    window.removeEventListener('storage', this.handleStorageChange);
  },
  computed: {
    isAuthenticated() {
      return this.localAuth;
    },
    isAdmin() {
      return this.localUser ? this.localUser.is_admin : false;
    },
    userName() {
      return this.localUser ? (this.localUser.full_name || this.localUser.username) : '';
    }
  },
  methods: {
    getUserData() {
      try {
        const userData = localStorage.getItem('user');
        return userData ? JSON.parse(userData) : null;
      } catch (e) {
        console.error('Error parsing user data:', e);
        return null;
      }
    },
    checkAuthStatus() {
      this.localAuth = !!localStorage.getItem('token');
      this.localUser = this.getUserData();
    },
    handleStorageChange(event) {
      if (event.key === 'token' || event.key === 'user') {
        this.checkAuthStatus();
      }
    },
    logout() {
      // Clear auth data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Update local state
      this.localAuth = false;
      this.localUser = null;
      
      // Notify other components about the auth change
      emitter.emit('auth-changed');
      
      // Redirect to login
      this.$router.push({ name: 'Login' });
    }
  }
}
</script>

<style scoped>
.router-link-exact-active {
  font-weight: bold;
}
</style> 