import axios from 'axios'
import { useLoadingStore } from '@/store/loadingStore'

const client = axios.create({
  baseURL: '/api',
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  useLoadingStore.getState().show()
  return config
})

client.interceptors.response.use(
  (response) => {
    useLoadingStore.getState().hide()
    return response
  },
  (error) => {
    useLoadingStore.getState().hide()
    return Promise.reject(error)
  }
)

export default client
