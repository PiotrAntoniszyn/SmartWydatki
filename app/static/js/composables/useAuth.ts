import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useApi } from './useApi';

/**
 * Authentication composable for managing user authentication state and actions
 */
export const useAuth = () => {
  const router = useRouter();
  const api = useApi();
  
  // State
  const token = ref<string | null>(localStorage.getItem('auth_token'));
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);
  
  // Computed
  const isAuthenticated = computed<boolean>(() => !!token.value);
  
  /**
   * Set token in localStorage and state
   */
  const setToken = (newToken: string): void => {
    localStorage.setItem('auth_token', newToken);
    token.value = newToken;
  };
  
  /**
   * Clear token from localStorage and state
   */
  const clearToken = (): void => {
    localStorage.removeItem('auth_token');
    token.value = null;
  };
  
  /**
   * Login user with email and password
   */
  const login = async (email: string, password: string): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      // In a real implementation, this would call an API endpoint
      // const response = await api.post<{ token: string }>('/auth/login', { email, password });
      
      // For demo purposes, we'll simulate a successful login
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store the token
      setToken('demo_token');
      
      return true;
    } catch (err) {
      error.value = 'Nieprawidłowy email lub hasło';
      console.error('Login error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Register a new user
   */
  const register = async (userData: { name: string; email: string; password: string }): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      // In a real implementation, this would call an API endpoint
      // const response = await api.post<{ token: string }>('/auth/register', userData);
      
      // For demo purposes, we'll simulate a successful registration
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store the token
      setToken('demo_token');
      
      return true;
    } catch (err) {
      error.value = 'Wystąpił błąd podczas rejestracji. Spróbuj ponownie.';
      console.error('Registration error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Logout the current user
   */
  const logout = (): void => {
    clearToken();
    router.push('/login');
  };
  
  /**
   * Check if user is authenticated and redirect if not
   */
  const requireAuth = (): boolean => {
    if (!isAuthenticated.value) {
      router.push('/login');
      return false;
    }
    return true;
  };
  
  return {
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    requireAuth
  };
}; 