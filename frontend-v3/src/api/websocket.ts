/**
 * WebSocket Client for TARS real-time updates
 * Protocol: Backend uses {command, params} for requests
 *           Backend sends {success, type, data} for responses
 */

type MessageHandler = (data: any) => void
type ConnectionHandler = () => void

interface WebSocketMessage {
  success: boolean
  server_id?: string
  type?: string
  [key: string]: any
}

class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectInterval = 5000
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private messageHandlers: Map<string, MessageHandler[]> = new Map()
  private connectionHandlers: ConnectionHandler[] = []
  private disconnectionHandlers: ConnectionHandler[] = []
  private isManualClose = false
  private activeStreams: Set<string> = new Set()

  constructor() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.DEV
      ? window.location.hostname + ':8888'
      : '192.168.1.220:8888'
    this.url = `${protocol}//${host}/ws`
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.isManualClose = false
    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      console.log('[WS] Connected to TARS')
      this.connectionHandlers.forEach(handler => handler())

      // Clear reconnect timer on successful connection
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
        this.reconnectTimer = null
      }

      // Restart active streams after reconnection
      this.restartStreams()
    }

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)

        // Backend sends messages with 'type' field indicating data type
        // e.g., {success: true, type: "workers", workers: [...]}
        if (message.type) {
          const handlers = this.messageHandlers.get(message.type) || []
          // Pass the entire message to handlers (they can extract specific fields)
          handlers.forEach(handler => handler(message))
        }
      } catch (error) {
        console.error('[WS] Failed to parse message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('[WS] Error:', error)
    }

    this.ws.onclose = () => {
      console.log('[WS] Disconnected from TARS')
      this.disconnectionHandlers.forEach(handler => handler())

      // Auto-reconnect unless manually closed
      if (!this.isManualClose) {
        this.scheduleReconnect()
      }
    }
  }

  disconnect() {
    this.isManualClose = true
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    // Stop all active streams before disconnect
    this.stopAllStreams()

    this.ws?.close()
    this.ws = null
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) {
      return
    }

    console.log(`[WS] Reconnecting in ${this.reconnectInterval / 1000}s...`)
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, this.reconnectInterval)
  }

  private restartStreams() {
    // Restart all active streams after reconnection
    this.activeStreams.forEach(stream => {
      this.sendCommand(`start_${stream}`)
    })
  }

  private stopAllStreams() {
    this.activeStreams.forEach(stream => {
      this.sendCommand(`stop_${stream}`)
    })
    this.activeStreams.clear()
  }

  /**
   * Start streaming data from backend
   * Available streams: workers_info, pending_tasks_info, completed_tasks_info, frontend_messages
   */
  startStream(streamName: string) {
    if (this.activeStreams.has(streamName)) {
      return
    }

    this.activeStreams.add(streamName)
    this.sendCommand(`start_${streamName}`)
  }

  /**
   * Stop streaming data from backend
   */
  stopStream(streamName: string) {
    this.activeStreams.delete(streamName)
    this.sendCommand(`stop_${streamName}`)
  }

  /**
   * Send command to backend
   * Backend expects: {command: "command_name", params: {...}}
   */
  private sendCommand(command: string, params: Record<string, any> = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ command, params }))
    } else {
      console.warn('[WS] Cannot send command - not connected')
    }
  }

  /**
   * Dismiss a frontend message by ID
   */
  dismissMessage(messageId: string) {
    this.sendCommand('dismiss_message', { message_id: messageId })
  }

  // Register handler for specific message type
  on(messageType: string, handler: MessageHandler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    this.messageHandlers.get(messageType)!.push(handler)
  }

  // Unregister handler
  off(messageType: string, handler: MessageHandler) {
    const handlers = this.messageHandlers.get(messageType)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  // Connection lifecycle handlers
  onConnect(handler: ConnectionHandler) {
    this.connectionHandlers.push(handler)
  }

  onDisconnect(handler: ConnectionHandler) {
    this.disconnectionHandlers.push(handler)
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsClient = new WebSocketClient()
export default wsClient
