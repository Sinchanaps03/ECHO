import axios from 'axios';

class ApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    // Add request interceptor
    this.api.interceptors.request.use(
      (config) => {
        console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
        return config;
      },
      (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor
    this.api.interceptors.response.use(
      (response) => {
        return response.data;
      },
      (error) => {
        console.error('API Error:', error);
        
        if (error.response) {
          // Server responded with error status
          const errorMessage = error.response.data?.error || error.response.data?.message || 'Server error';
          throw new Error(`${error.response.status}: ${errorMessage}`);
        } else if (error.request) {
          // Request was made but no response received
          throw new Error('Network error: No response from server');
        } else {
          // Something else happened
          throw new Error(`Request error: ${error.message}`);
        }
      }
    );
  }

  // Health check
  async healthCheck() {
    try {
      const response = await this.api.get('/health');
      return response;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // Process voice input
  async processVoice(formData) {
    try {
      const response = await axios.post(`${this.baseURL}/api/process-voice`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // Longer timeout for file upload and processing
      });
      
      return response.data;
    } catch (error) {
      console.error('Voice processing failed:', error);
      throw error;
    }
  }

  // Text to image conversion
  async textToImage(data) {
    try {
      console.log('ApiService.textToImage called with data:', data);
      console.log('Making request to:', `${this.baseURL}/api/text-to-image`);
      const response = await this.api.post('/api/text-to-image', data);
      console.log('ApiService received response:', response);
      return response;
    } catch (error) {
      console.error('Text to image conversion failed:', error);
      throw error;
    }
  }

  // Get session by ID
  async getSession(sessionId) {
    try {
      const response = await this.api.get(`/api/sessions/${sessionId}`);
      return response;
    } catch (error) {
      console.error('Failed to get session:', error);
      throw error;
    }
  }

  // Get recent sessions
  async getRecentSessions(limit = 10) {
    try {
      const response = await this.api.get(`/api/sessions?limit=${limit}`);
      return response;
    } catch (error) {
      console.error('Failed to get recent sessions:', error);
      throw error;
    }
  }

  // Search sessions
  async searchSessions(query, limit = 20) {
    try {
      const response = await this.api.get(`/api/search?q=${encodeURIComponent(query)}&limit=${limit}`);
      return response;
    } catch (error) {
      console.error('Failed to search sessions:', error);
      throw error;
    }
  }

  // Download image
  async downloadImage(imageUrl, filename) {
    try {
      const response = await axios.get(imageUrl, {
        responseType: 'blob',
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || 'echosketch-image.png');
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Failed to download image:', error);
      throw error;
    }
  }

  // Convert image to base64
  async imageToBase64(imageUrl) {
    try {
      const response = await axios.get(imageUrl, {
        responseType: 'arraybuffer',
      });

      const base64 = btoa(
        new Uint8Array(response.data).reduce(
          (data, byte) => data + String.fromCharCode(byte),
          ''
        )
      );

      return `data:image/png;base64,${base64}`;
    } catch (error) {
      console.error('Failed to convert image to base64:', error);
      throw error;
    }
  }

  // Get server statistics
  async getStatistics() {
    try {
      const response = await this.api.get('/api/stats');
      return response;
    } catch (error) {
      console.error('Failed to get statistics:', error);
      throw error;
    }
  }
}

// Export singleton instance
export default new ApiService();