// API service for Maya AI backend communication

export interface SSEEvent {
  type: 'status' | 'chunk' | 'code_chunk' | 'command' | 'code' | 'error' | 'explanation' | 'features' | 'suggestions' 
       | 'publish_status' | 'publish_success' | 'publish_error' | 'publish_message';
  payload: any;
}

export interface GameCode {
  html: string;
  css: string;
  js: string;
}

export interface ChatRequest {
  prompt: string;
  session_id?: string;
  user_id?: string;
}

class MayaAPIService {
  private baseURL = 'http://localhost:8000'; // The FastAPI server
  private currentController: AbortController | null = null;

  /**
   * Generate a game by streaming the response from the Maya agent.
   * @param request - The chat request containing the prompt
   * @param onEvent - Callback for each SSE event
   */
  async generateGame(
    request: ChatRequest,
    onEvent: (event: SSEEvent) => void
  ): Promise<void> {
    if (this.currentController) {
      this.currentController.abort();
    }
    this.currentController = new AbortController();
    
    const url = `${this.baseURL}/generate-game-real`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          prompt: request.prompt,
          session_id: request.session_id || this.generateSessionId(),
          user_id: request.user_id || 'frontend_user'
        }),
        signal: this.currentController.signal,
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last incomplete line in buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); // Remove 'data: ' prefix
            
            if (data === '[DONE]') {
              // Stream completed
              return;
            }

            try {
              const event: SSEEvent = JSON.parse(data);
              onEvent(event);
            } catch (error) {
              console.warn('Failed to parse SSE event:', data);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        // Request was cancelled, ignore
        return;
      }
      
      // Send error event
      onEvent({
        type: 'error',
        payload: `Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      this.currentController = null;
    }
  }

  /**
   * Cancel the current request
   */
  cancelRequest(): void {
    if (this.currentController) {
      this.currentController.abort();
      this.currentController = null;
    }
  }

  /**
   * Check if the API is healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export const mayaAPI = new MayaAPIService();