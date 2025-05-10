<template>
  <div
    class="modal fade"
    ref="confirmModal"
    tabindex="-1"
    aria-labelledby="confirmModalLabel"
    aria-hidden="true"
    :data-bs-backdrop="props.persistent ? 'static' : true"
    :data-bs-keyboard="props.persistent ? 'false' : 'true'"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="confirmModalLabel">{{ title }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Zamknij"></button>
        </div>
        <div class="modal-body">
          <p>{{ message }}</p>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-secondary" 
            data-bs-dismiss="modal"
          >
            Anuluj
          </button>
          <button 
            type="button" 
            class="btn btn-danger" 
            @click="handleConfirm"
          >
            {{ confirmButtonText }}
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

const props = defineProps<{
  title: string;
  message: string;
  confirmButtonText: string;
  persistent?: boolean;
}>();

const emit = defineEmits<{
  (e: 'confirm'): void
}>();

const confirmModal = ref<HTMLElement | null>(null);
let modal: BootstrapModal | null = null;

onMounted(() => {
  if (confirmModal.value) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    if (w.bootstrap) {
      const options = props.persistent ? { backdrop: 'static', keyboard: false } : undefined;
      modal = new w.bootstrap.Modal(confirmModal.value, options);
    }
  }
});

// Handle confirm button click
const handleConfirm = () => {
  modal?.hide();
  emit('confirm');
};

// Public method to open the modal
const open = () => {
  modal?.show();
};

// Expose methods to parent component
defineExpose({
  open
});
</script>

<style scoped>
/* Using Bootstrap's built-in styles */
</style> 