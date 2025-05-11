import { ref, computed } from 'vue';
import { useApi } from './useApi';
import { CategorySuggestionDTO, CategorySuggestionVM, UseOnboardingSuggestions } from '../types/onboarding';

/**
 * Composable for fetching and managing category suggestions for onboarding
 */
export const useOnboardingSuggestions = (): UseOnboardingSuggestions => {
  const api = useApi();
  
  // State
  const suggestions = ref<CategorySuggestionVM[]>([]);
  const loading = ref<boolean>(false);
  const errorMessage = ref<string | null>(null);
  const selectedIds = ref<string[]>([]);
  
  // Computed
  const canContinue = computed<boolean>(() => {
    const count = selectedIds.value.length;
    return count >= 1 && count <= 5;
  });
  
  /**
   * Maps a DTO from the API to our view model
   */
  const mapToViewModel = (dto: CategorySuggestionDTO): CategorySuggestionVM => ({
    id: dto.id,
    name: dto.name,
    usageCount: dto.usage_count
  });
  
  /**
   * Fetches category suggestions from the API
   */
  const fetchSuggestions = async (): Promise<void> => {
    loading.value = true;
    errorMessage.value = null;
    
    try {
      const response = await api.get<CategorySuggestionDTO[]>('/categories/initial-suggestions');
      
      suggestions.value = response.map(mapToViewModel);
      
      // Handle empty suggestions case
      if (suggestions.value.length === 0) {
        errorMessage.value = 'Brak propozycji kategorii';
      }
    } catch (error) {
      errorMessage.value = 'Usługa niedostępna, spróbuj ponownie później.';
      console.error('Failed to fetch suggestions:', error);
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Toggles selection of a category suggestion
   */
  const toggleSelection = (id: string): void => {
    const index = selectedIds.value.indexOf(id);
    
    if (index === -1) {
      // Don't add if we already have 5 selected
      if (selectedIds.value.length >= 5) {
        return;
      }
      selectedIds.value.push(id);
    } else {
      selectedIds.value.splice(index, 1);
    }
  };
  
  return {
    suggestions,
    loading,
    errorMessage,
    selectedIds,
    fetchSuggestions,
    toggleSelection,
    canContinue
  };
}; 