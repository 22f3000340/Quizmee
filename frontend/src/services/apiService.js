import API_CONFIG from '../config/api.js';

/**
 * API Service using the native Fetch API
 */
const ApiService = {
  /**
   * Base request method for all API calls
   * @param {string} endpoint - API endpoint path
   * @param {Object} options - Fetch options
   * @returns {Promise<any>} - API response
   */
  async request(endpoint, options = {}) {
    // Fix double slash if needed
    let fixedEndpoint = endpoint;
    if (endpoint.startsWith('/') && API_CONFIG.BASE_URL.endsWith('/')) {
      fixedEndpoint = endpoint.substring(1);
      console.log(`Fixed double slash in endpoint: ${endpoint} -> ${fixedEndpoint}`);
    }
    
    const url = API_CONFIG.BASE_URL + fixedEndpoint;
    console.log(`Constructing URL: ${API_CONFIG.BASE_URL} + ${fixedEndpoint} = ${url}`);
    
    // Default headers
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Merge options
    const fetchOptions = {
      ...options,
      headers,
      credentials: 'include'
    };
    
    // Set timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
    fetchOptions.signal = controller.signal;
    
    try {
      console.log(`Making ${options.method || 'GET'} request to ${url}`);
      if (options.method === 'POST' || options.method === 'PUT') {
        console.log('Request payload:', options.body);
      }
      
      const response = await fetch(url, fetchOptions);
      
      // Clear timeout
      clearTimeout(timeoutId);
      
      // Handle authentication errors
      if (response.status === 401 || response.status === 403) {
        // Clear invalid token
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // Emit auth change event if available
        if (typeof window.emitter !== 'undefined') {
          window.emitter.emit('auth-changed');
        }
        
        throw new Error('Authentication failed. Please log in again.');
      }
      
      // Handle other API error responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API Error:', response.status, errorData);
        throw new Error(errorData.msg || errorData.message || `Request failed with status ${response.status}`);
      }
      
      // Handle empty responses
      if (response.status === 204) {
        return null;
      }
      
      // Parse JSON response
      return await response.json();
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timed out');
      }
      throw error;
    }
  },
  
  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @param {Object} params - URL parameters
   * @returns {Promise<any>} - API response
   */
  get(endpoint, params = {}) {
    // Add query parameters if any
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value);
      }
    });
    
    const queryString = queryParams.toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, { method: 'GET' });
  },
  
  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<any>} - API response
   */
  post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<any>} - API response
   */
  put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },
  
  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<any>} - API response
   */
  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};

export default ApiService; 