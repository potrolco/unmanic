/**
 * TARS API Type Definitions
 * Generated from unmanic/webserver/api_v2/schema
 */

export interface Worker {
  id: string
  name: string
  idle: boolean
  paused: boolean
  current_file?: string
  current_task?: number
  start_time?: string
  current_command?: string
  log_lines?: string[]
}

export interface QueueTask {
  id: number
  library_id: number
  abspath: string
  priority: number
  created_at: string
}

export interface HistoryTask {
  id: number
  task_label: string
  task_success: boolean
  finish_time: string
  abspath: string
}

export interface Plugin {
  plugin_id: string
  name: string
  author: string
  version: string
  description: string
  icon?: string
  tags?: string[]
}

export interface Settings {
  number_of_workers: number
  cache_path: string
  library_path: string
  enable_hardware_acceleration: boolean
  gpu_enabled?: boolean
  gpu_assignment_strategy?: string
  gpu_max_workers_per_device?: number
}

export interface GPUDevice {
  device_id: string
  device_type: string
  available: boolean
  worker_id?: string
  allocated_at?: number
}

export interface GPUStatus {
  enabled: boolean
  total_devices: number
  available_devices: number
  active_allocations: number
  max_workers_per_device: number
  strategy: string
  devices: GPUDevice[]
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  recordsTotal: number
  recordsFiltered: number
}
