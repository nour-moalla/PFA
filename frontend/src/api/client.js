import axios from 'axios'
import { auth } from '../config/firebase'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(async (config) => {
  const user = auth.currentUser
  if (user) {
    const token = await user.getIdToken()
    config.headers = {
      ...(config.headers || {}),
      Authorization: `Bearer ${token}`,
    }
  }
  return config
})

// Resume endpoints
export const resumeAPI = {
  upload: (file, options = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    if (options.job_description) formData.append('job_description', options.job_description)
    if (options.job_title) formData.append('job_title', options.job_title)
    if (options.company) formData.append('company', options.company)
    if (options.experience) formData.append('experience', options.experience)
    return apiClient.post('/api/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  analyze: (file, options = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    if (options.job_description) formData.append('job_description', options.job_description)
    if (options.job_title) formData.append('job_title', options.job_title)
    if (options.company) formData.append('company', options.company)
    if (options.experience) formData.append('experience', options.experience)
    return apiClient.post('/api/resume/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  extractSkills: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/resume/extract-skills', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// Interview endpoints
export const interviewAPI = {
  start: (data) => apiClient.post('/api/interview/start', data),
  answer: (data) => apiClient.post('/api/interview/answer', data),
  getHistory: (sessionId) => apiClient.get(`/api/interview/history/${sessionId}`),
  getScores: (sessionId) => apiClient.get(`/api/interview/scores/${sessionId}`),
  requestCodeQuestion: (sessionId) => apiClient.post(`/api/interview/code-question/${sessionId}`),
}

// Career insights endpoints
export const careerAPI = {
  getMarketInsights: () => apiClient.get('/api/career/market-insights'),
  uploadCV: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/career/upload-cv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  analyze: (data) => apiClient.post('/api/career/analyze', data),
  clusterSkills: (data) => apiClient.post('/api/career/cluster-skills', data),
  downloadPDF: (filename) => apiClient.get(`/api/career/download/${filename}`, { responseType: 'blob' }),
}

// Job matching endpoints
export const jobAPI = {
  matchCV: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/jobs/match-cv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getDatabaseInfo: () => apiClient.get('/api/jobs/database-info'),
}

export default apiClient

