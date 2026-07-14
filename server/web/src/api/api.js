import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  login: (username, password) => api.post('/token', { username, password }),
  register: (username, password) => api.post('/register', { username, password })
}

export const clients = {
  getAll: () => api.get('/clients'),
  getActions: (clientId, limit = 100) => api.get(`/clients/${clientId}/actions?limit=${limit}`)
}

export const actions = {
  getAll: (limit = 100, offset = 0, actionType = null) => {
    let url = `/actions?limit=${limit}&offset=${offset}`
    if (actionType) url += `&action_type=${actionType}`
    return api.get(url)
  }
}

export const ai = {
  getExtracted: (infoType = null, limit = 100) => {
    let url = `/ai/extracted?limit=${limit}`
    if (infoType) url += `&info_type=${infoType}`
    return api.get(url)
  }
}

export const dashboard = {
  getStats: () => api.get('/dashboard/stats')
}

export const videos = {
  getByClient: (clientId) => api.get(`/clients/${clientId}/videos`),
  download: (videoId) => api.get(`/videos/${videoId}`, { responseType: 'blob' })
}

export default api
