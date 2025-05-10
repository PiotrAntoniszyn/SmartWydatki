<template>
  <div class="modal fade" ref="errorModal" tabindex="-1" aria-labelledby="errorModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title" id="errorModalLabel">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Wystąpił błąd
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Zamknij"></button>
        </div>
        <div class="modal-body">
          <p>{{ errorMessage }}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button 
            type="button" 
            class="btn btn-primary"
            @click="handleRetry"
          >
            <i class="bi bi-arrow-clockwise me-1"></i> Spróbuj ponownie
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
// Import type only to avoid linter errors
import type { Modal as BootstrapModal } from 'bootstrap';

const errorModal = ref<HTMLElement | null>(null);
const errorMessage = ref<string>('Wystąpił błąd podczas ładowania danych.');
let modal: BootstrapModal | null = null;

const emit = defineEmits<{
  (e: 'retry'): void
}>();

onMounted(() => {
  if (errorModal.value) {
    // Use the global Bootstrap object to create a modal
    // This avoids having to import the entire Bootstrap library
    if (window.bootstrap) {
      modal = new window.bootstrap.Modal(errorModal.value);
    }
  }
});

// Handle retry button click
const handleRetry = () => {
  modal?.hide();
  emit('retry');
};

// Public method to open the modal with a custom message
const open = (message: string) => {
  errorMessage.value = message || 'Wystąpił błąd podczas ładowania danych.';
  modal?.show();
};

// Expose methods to parent component
defineExpose({
  open
});
</script>

<style scoped>
/* No additional styling needed - using Bootstrap's built-in styles */
</style> 