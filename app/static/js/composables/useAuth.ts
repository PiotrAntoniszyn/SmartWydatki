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
      const response = await api.post<{ token: string }>('/auth/login', { email, password });
      if (response.token) {
        setToken(response.token);
        return true;
      } else {
        error.value = 'Brak tokenu w odpowiedzi';
        return false;
      }
    } catch (err) {
      error.value = typeof err === 'string' ? err : 'Nieprawidłowy email lub hasło';
      console.error('Login error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Register a new user
   */
  const register = async (userData: { name?: string; email: string; password: string; passwordConfirm?: string }): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.post<{ token: string }>('/auth/register', {
        email: userData.email,
        password: userData.password,
        passwordConfirm: userData.passwordConfirm
      });
      if (response.token) {
        setToken(response.token);
        return true;
      } else {
        error.value = 'Brak tokenu w odpowiedzi';
        return false;
      }
    } catch (err) {
      error.value = typeof err === 'string' ? err : 'Wystąpił błąd podczas rejestracji. Spróbuj ponownie.';
      console.error('Registration error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Logout the current user
   */
  const logout = async (): Promise<void> => {
    try {
      await api.post('/auth/logout', {});
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      clearToken();
      router.push('/login');
    }
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