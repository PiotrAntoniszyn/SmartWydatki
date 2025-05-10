<template>
  <div class="pagination-controls d-flex justify-content-between align-items-center my-3">
    <div class="pagination-info">
      Strona {{ pagination.currentPage }} z {{ pagination.totalPages || 1 }}
      ({{ pagination.total }} {{ formatItemsLabel(pagination.total) }})
    </div>
    
    <div class="pagination-buttons">
      <button
        type="button"
        id="prev-page"
        class="btn btn-outline-secondary me-2"
        :disabled="pagination.currentPage <= 1"
        @click="handlePrevPage"
        aria-label="Poprzednia strona"
      >
        <i class="bi bi-chevron-left"></i> Poprzednia
      </button>
      
      <button
        type="button"
        id="next-page"
        class="btn btn-outline-secondary"
        :disabled="pagination.currentPage >= pagination.totalPages"
        @click="handleNextPage"
        aria-label="Następna strona"
      >
        Następna <i class="bi bi-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import type { PaginationVM } from '../types/expenses';

const props = defineProps<{
  pagination: PaginationVM
}>();

const emit = defineEmits<{
  (e: 'change-page', offset: number): void
}>();

// Handle pagination navigation
const handlePrevPage = () => {
  if (props.pagination.currentPage > 1) {
    const newOffset = (props.pagination.currentPage - 2) * props.pagination.limit;
    emit('change-page', newOffset);
  }
};

const handleNextPage = () => {
  if (props.pagination.currentPage < props.pagination.totalPages) {
    const newOffset = props.pagination.currentPage * props.pagination.limit;
    emit('change-page', newOffset);
  }
};

// Format items label based on count
const formatItemsLabel = (count: number): string => {
  if (count === 1) return 'wydatek';
  if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return 'wydatki';
  return 'wydatków';
};
</script>

<style scoped>
.pagination-controls {
  margin-top: 1.5rem;
}

@media (max-width: 576px) {
  .pagination-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .pagination-info {
    text-align: center;
    width: 100%;
  }
  
  .pagination-buttons {
    display: flex;
    width: 100%;
  }
  
  .pagination-buttons button {
    flex: 1;
  }
}
</style> 