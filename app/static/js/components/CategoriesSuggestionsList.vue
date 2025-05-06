<template>
  <div class="categories-suggestions-list">
    <h2 class="text-h5 mb-4">Wybierz od 1 do 5 kategorii, aby rozpocząć</h2>
    
    <p class="text-subtitle-1 mb-6">
      Te kategorie pomogą nam lepiej dopasować sugestie do Twoich potrzeb.
      Możesz je później zmienić w ustawieniach.
    </p>
    
    <div class="selection-count mb-4" :class="{ 'error-text': isInvalid }">
      Wybrano: {{ selectedIds.length }}/5
      <span v-if="isInvalid" class="error-message">
        (wybierz przynajmniej 1 kategorię)
      </span>
    </div>
    
    <v-chip-group
      v-model="selectedModel"
      multiple
      column
      class="categories-chips"
      :max="5"
      selected-class="selected-chip"
    >
      <v-chip
        v-for="item in items"
        :key="item.id"
        :value="item.id"
        filter
        variant="elevated"
        class="category-chip ma-2"
        :aria-label="`Kategoria ${item.name}, wybrana ${isSelected(item.id) ? 'tak' : 'nie'}`"
      >
        {{ item.name }}
        <span class="usage-count">{{ formatUsageCount(item.usageCount) }}</span>
      </v-chip>
    </v-chip-group>
    
    <div v-if="selectedIds.length >= 5" class="text-caption text-center mt-4">
      Osiągnięto maksymalną liczbę wyborów (5). Odznacz niektóre, aby wybrać inne.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import { CategorySuggestionVM } from '../types/onboarding';

const props = defineProps<{
  items: CategorySuggestionVM[];
  selectedIds: string[];
}>();

const emit = defineEmits<{
  'update:selectedIds': [selectedIds: string[]];
}>();

// Computed property for v-model binding with v-chip-group
const selectedModel = computed({
  get: () => props.selectedIds,
  set: (newValue: string[]) => {
    emit('update:selectedIds', newValue);
  }
});

// Check if selection is invalid (when value is shown)
const isInvalid = computed(() => {
  return props.selectedIds.length === 0;
});

// Helper to check if item is selected (for aria-label)
const isSelected = (id: string): boolean => {
  return props.selectedIds.includes(id);
};

// Format usage count for display
const formatUsageCount = (count: number): string => {
  if (count === 0) return '';
  return `(${count})`;
};
</script>

<style scoped>
.categories-suggestions-list {
  max-width: 600px;
  margin: 0 auto;
}

.categories-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.category-chip {
  font-size: 1rem;
  padding: 0.75rem 1rem;
  margin: 0.5rem;
}

.selected-chip {
  background-color: var(--v-primary-base, #1976d2) !important;
  color: white !important;
}

.usage-count {
  font-size: 0.75rem;
  margin-left: 0.25rem;
  opacity: 0.7;
}

.selection-count {
  text-align: center;
  font-weight: 500;
}

.error-text {
  color: var(--v-error-base, #ff5252);
}

.error-message {
  margin-left: 0.5rem;
}
</style> 