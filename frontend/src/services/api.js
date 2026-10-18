import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dsarApi = {
  // Health check
  health: () => api.get('/health'),
  
  // Create DSAR request
  createRequest: (data) => api.post('/api/dsar/requests', data),
  
  // List all DSAR requests
  listRequests: (skip = 0, limit = 100) => api.get(`/api/dsar/requests?skip=${skip}&limit=${limit}`),
  
  // Get specific request
  getRequest: (id) => api.get(`/api/dsar/requests/${id}`),
  
  // Process request (admin)
  processRequest: (id) => api.post(`/api/dsar/requests/${id}/process`),
  
  // Download export
  downloadExport: (id, format = 'json') => api.get(`/api/dsar/requests/${id}/export?format=${format}`, {
    responseType: 'blob',
  }),
};

export default api;
