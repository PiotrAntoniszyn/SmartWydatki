/**
 * Composable for making authenticated API requests
 */

// Simple API client for authenticated requests
export const useApi = () => {
  
  const getAuthHeader = (): Record<string, string> => {
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
  const get = async <T>(endpoint: string, params?: Record<string, string | number | boolean | null | undefined>): Promise<T> => {
    try {
      const url = new URL(endpoint, window.location.origin);
      
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== null && value !== undefined) {
            url.searchParams.append(key, String(value));
          }
        });
      }
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      };

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
        credentials: 'include'
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
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        credentials: 'include',
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

  /**
   * Makes a PUT request to the API
   * @param endpoint - The API endpoint to call
   * @param data - The data to send
   * @returns Promise with the response data
   */
  const put = async <T>(endpoint: string, data: any): Promise<T> => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      };

      const response = await fetch(endpoint, {
        method: 'PUT',
        headers,
        credentials: 'include',
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

  /**
   * Makes a DELETE request to the API
   * @param endpoint - The API endpoint to call
   * @returns Promise with the response data
   */
  const del = async <T>(endpoint: string): Promise<T> => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      };

      const response = await fetch(endpoint, {
        method: 'DELETE',
        headers,
        credentials: 'include'
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
    post,
    put,
    delete: del // Using 'del' as variable name because 'delete' is a reserved keyword
  };
}; 