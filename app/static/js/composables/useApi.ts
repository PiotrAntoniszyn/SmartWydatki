/**
 * Composable for making authenticated API requests
 */

// Simple API client for authenticated requests
export const useApi = () => {
  
  const getAuthHeader = () => {
    // In a real application, this would get the auth token from localStorage or a store
    const token = localStorage.getItem('auth_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  /**
   * Makes a GET request to the API
   * @param endpoint - The API endpoint to call
   * @param params - Optional query parameters
   * @returns Promise with the response data
   */
  const get = async <T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T> => {
    try {
      const url = new URL(endpoint, window.location.origin);
      
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          url.searchParams.append(key, String(value));
        });
      }
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader()
        }
      });

      // Unauthorized, redirect to login
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  };

  /**
   * Makes a POST request to the API
   * @param endpoint - The API endpoint to call
   * @param data - The data to send
   * @returns Promise with the response data
   */
  const post = async <T>(endpoint: string, data: any): Promise<T> => {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader()
        },
        body: JSON.stringify(data)
      });
      
      // Unauthorized, redirect to login
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  };

  return {
    get,
    post
  };
}; 