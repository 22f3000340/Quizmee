export const AuthMixin = {
  data() {
    return {
      currentUser: null,
      token: localStorage.getItem('token') || null,
      apiBaseUrl: 'http://localhost:5000/api'
    }
  },
  created() {
    // Check if user is already logged in
    const userData = localStorage.getItem('user')
    if (userData) {
      this.currentUser = JSON.parse(userData)
    }
  },
  methods: {
    async login(username, password) {
      try {
        const response = await fetch(`${this.apiBaseUrl}/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username, password })
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.msg || 'Login failed')
        }
        
        const data = await response.json()
        this.token = data.access_token
        this.currentUser = data.user
        
        // Store in localStorage
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.currentUser))
        
        return data
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },
    
    logout() {
      this.token = null
      this.currentUser = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Redirect to login page if not already there
      if (this.$route && this.$route.name !== 'Login') {
        this.$router.push({ name: 'Login' })
      }
    },
    
    isAuthenticated() {
      return !!this.token && !!this.currentUser
    },
    
    isAdmin() {
      return this.isAuthenticated() && this.currentUser.is_admin
    },
    
    getAuthHeaders() {
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      }
    },
    
    async fetchWithAuth(url, options = {}) {
      if (!this.token) {
        throw new Error('Authentication required')
      }
      
      const headers = {
        ...options.headers,
        'Authorization': `Bearer ${this.token}`
      }
      
      try {
        const response = await fetch(url, {
          ...options,
          headers
        })
        
        if (response.status === 401) {
          // Token expired or invalid
          this.logout()
          throw new Error('Authentication expired. Please login again.')
        }
        
        return response
      } catch (error) {
        console.error('API request error:', error)
        throw error
      }
    }
  }
} 