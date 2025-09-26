import io from 'socket.io-client';

class SocketService {
  constructor() {
    this.socket = null;
    this.url = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';
  }

  connect() {
    try {
      this.socket = io(this.url, {
        transports: ['websocket', 'polling'],
        timeout: 20000,
        forceNew: true
      });

      this.socket.on('connect', () => {
        console.log('Socket connected:', this.socket.id);
      });

      this.socket.on('disconnect', (reason) => {
        console.log('Socket disconnected:', reason);
      });

      this.socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
      });

      return this.socket;
    } catch (error) {
      console.error('Failed to initialize socket connection:', error);
      return null;
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event, data) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  isConnected() {
    return this.socket && this.socket.connected;
  }
}

// Export singleton instance
export default new SocketService();