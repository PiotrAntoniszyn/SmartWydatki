import { Ref, ComputedRef } from 'vue';

/**
 * Type definitions for the onboarding component
 */

// DTO received from API
export interface CategorySuggestionDTO {
  id: string;
  name: string;
  usage_count: number;
}

// ViewModel used in component
export interface CategorySuggestionVM {
  id: string;
  name: string;
  usageCount: number;
}

// Hook / composable state
export interface UseOnboardingSuggestions {
  suggestions: Ref<CategorySuggestionVM[]>;
  loading: Ref<boolean>;
  errorMessage: Ref<string|null>;
  selectedIds: Ref<string[]>;
  fetchSuggestions: () => Promise<void>;
  toggleSelection: (id: string) => void;
  canContinue: ComputedRef<boolean>;
} 