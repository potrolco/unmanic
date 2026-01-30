import axios, { type AxiosInstance } from 'axios'

/**
 * API Client for TARS backend
 * Base URL determined by Vite proxy in dev, direct in production
 */
class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.DEV ? '/unmanic/api' : '/unmanic/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error)
        return Promise.reject(error)
      }
    )
  }

  // Workers API
  async getWorkers() {
    return this.client.get('/v2/workers/status')
  }

  async pauseWorker(workerId: string) {
    return this.client.post(`/v2/workers/${workerId}/pause`)
  }

  async resumeWorker(workerId: string) {
    return this.client.post(`/v2/workers/${workerId}/resume`)
  }

  // Queue API
  async getQueue(start = 0, length = 50) {
    return this.client.post('/v2/pending/tasks', { start, length })
  }

  async deleteQueueTask(taskId: number) {
    return this.client.delete(`/v2/pending/tasks/${taskId}`)
  }

  async bulkDeleteCompleted() {
    return this.client.post('/v2/history/bulk_delete_completed')
  }

  // History API
  async getHistory(start = 0, length = 50) {
    return this.client.post('/v2/history/tasks', { start, length })
  }

  // Plugins API
  async getPlugins() {
    return this.client.post('/v2/plugins/installed', {})
  }

  async installPlugin(pluginId: string) {
    return this.client.post('/v2/plugins/install', { plugin_id: pluginId })
  }

  // Settings API
  async getSettings() {
    return this.client.get('/v2/settings/read')
  }

  async updateSettings(settings: Record<string, any>) {
    return this.client.post('/v2/settings/write', settings)
  }

  // GPU API (Phase 3)
  async getGPUStatus() {
    return this.client.get('/v2/health/gpu')
  }

  // Health Check
  async healthCheck() {
    return this.client.get('/v2/health')
  }
}

export const apiClient = new ApiClient()
export default apiClient
