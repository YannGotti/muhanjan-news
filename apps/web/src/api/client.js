import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 20000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('mn_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const url = error?.config?.url || ''

    if (status === 401 && !url.includes('/auth/login')) {
      localStorage.removeItem('mn_token')
    }

    return Promise.reject(error)
  },
)

export default api
