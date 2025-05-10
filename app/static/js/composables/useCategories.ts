import { ref } from 'vue';
import { useApi } from './useApi';
import type { CategoryVM, CategoryFormPayload } from '../types/categories';

interface ApiState<T> {
  data: T | undefined;
  loading: boolean;
  error: string | undefined;
}

export function useCategories() {
  const api = useApi();

  // Reactive state
  const categories = ref<CategoryVM[]>([]);
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // ============== Helpers ==================
  const setError = (msg: string) => {
    error.value = msg;
  };

  const clearError = () => {
    error.value = null;
  };

  // ============== CRUD =====================
  async function fetch() {
    loading.value = true;
    clearError();

    try {
      const response = await api.get<CategoryVM[]>('/categories');
      categories.value = response as unknown as CategoryVM[]; // API returns array of CategoryRead
    } catch (err: any) {
      setError('Nie udało się pobrać kategorii');
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function create(payload: CategoryFormPayload): Promise<boolean> {
    clearError();
    try {
      const isUnique = await checkNameUnique(payload.name);
      if (!isUnique) {
        setError('Kategoria o tej nazwie już istnieje');
        return false;
      }
      const newCategory = await api.post<CategoryVM>('/categories', payload);
      categories.value.push(newCategory as unknown as CategoryVM);
      return true;
    } catch (err: any) {
      if (err?.message?.includes('409')) {
        setError('Kategoria o tej nazwie już istnieje');
      } else {
        setError('Nie udało się utworzyć kategorii');
      }
      console.error(err);
      return false;
    }
  }

  async function update(id: string, payload: CategoryFormPayload): Promise<boolean> {
    clearError();
    try {
      const isUnique = await checkNameUnique(payload.name, id);
      if (!isUnique) {
        setError('Kategoria o tej nazwie już istnieje');
        return false;
      }
      const updated = await api.put<CategoryVM>(`/categories/${id}`, payload);
      // Replace in list
      const idx = categories.value.findIndex(c => c.id === id);
      if (idx !== -1) {
        categories.value[idx] = updated as unknown as CategoryVM;
      }
      return true;
    } catch (err: any) {
      if (err?.message?.includes('409')) {
        setError('Kategoria o tej nazwie już istnieje');
      } else {
        setError('Nie udało się zaktualizować kategorii');
      }
      console.error(err);
      return false;
    }
  }

  async function remove(id: string): Promise<boolean> {
    clearError();
    try {
      await api.delete(`/categories/${id}`);
      categories.value = categories.value.filter(c => c.id !== id);
      return true;
    } catch (err) {
      setError('Nie udało się usunąć kategorii');
      console.error(err);
      return false;
    }
  }

  // ============== Validation ===============
  /**
   * Checks if category name is unique among current categories.
   * Uses cached list first; if list empty, fetches from API.
   */
  async function checkNameUnique(name: string, excludeId?: string): Promise<boolean> {
    // If we don\'t have data yet, fetch first
    if (categories.value.length === 0) {
      try {
        await fetch();
      } catch {
        // ignore error; uniqueness will fallback to optimistic
      }
    }

    const existsLocally = categories.value.some(c => c.name.trim().toLowerCase() === name.trim().toLowerCase() && c.id !== excludeId);
    if (existsLocally) return false;

    // Fallback to API check if list may be incomplete
    try {
      const remote = await api.get<CategoryVM[]>(`/categories?name=${encodeURIComponent(name)}`);
      if (Array.isArray(remote) && remote.length > 0) {
        const collision = remote.some(c => c.name.trim().toLowerCase() === name.trim().toLowerCase() && c.id !== excludeId);
        return !collision;
      }
      return true;
    } catch (err) {
      // If API fails, assume unique to allow optimistic create; backend will enforce
      console.warn('Uniqueness check failed, assuming unique', err);
      return true;
    }
  }

  return {
    categories,
    loading,
    error,
    fetch,
    create,
    update,
    remove,
    checkNameUnique,
  };
} 