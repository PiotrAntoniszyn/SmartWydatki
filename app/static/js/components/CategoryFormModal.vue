<template>
  <div
    class="modal fade"
    ref="categoryModal"
    tabindex="-1"
    aria-labelledby="categoryModalLabel"
    aria-hidden="true"
    data-bs-backdrop="static"  <!-- persistent modal: no close on outside click -->
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="categoryModalLabel">
            <i class="bi" :class="isEditMode ? 'bi-pencil' : 'bi-plus-lg'" aria-hidden="true"></i>
            {{ isEditMode ? 'Edytuj kategorię' : 'Dodaj kategorię' }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Zamknij"></button>
        </div>
        <div class="modal-body">
          <form id="category-form" @submit.prevent="saveCategory">
            <!-- Name field -->
            <div class="mb-3">
              <label for="category-name" class="form-label required">Nazwa kategorii</label>
              <input
                type="text"
                class="form-control"
                id="category-name"
                v-model="formData.name"
                maxlength="30"
                required
                :class="{ 'is-invalid': validationErrors.name }"
              />
              <div class="form-text text-end">{{ formData.name.length }}/30</div>
              <div class="invalid-feedback" v-if="validationErrors.name">
                {{ validationErrors.name }}
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Anuluj</button>
          <button type="submit" form="category-form" class="btn btn-primary">
            <i class="bi bi-save me-1" aria-hidden="true"></i>
            Zapisz
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import type { CategoryVM, CategoryFormPayload } from '../types/categories';
import { useCategories } from '../composables/useCategories';
import type { Modal as BootstrapModal } from 'bootstrap';

const emit = defineEmits<{
  (e: 'saved'): void;
}>();

// Composable
const {
  create: createCategory,
  update: updateCategory,
  checkNameUnique,
} = useCategories();

// Modal reference and instance
const categoryModal = ref<HTMLElement | null>(null);
let modal: BootstrapModal | null = null;

// State
const mode = ref<'create' | 'edit'>('create');
const originalCategory = ref<CategoryVM | null>(null);
const formData = reactive<CategoryFormPayload>({
  name: '',
});

const validationErrors = reactive({
  name: '',
});

const isEditMode = computed(() => mode.value === 'edit');

onMounted(() => {
  // Explicit cast to any to satisfy TS until global types are available
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = window as any;
  if (categoryModal.value && w.bootstrap) {
    modal = new w.bootstrap.Modal(categoryModal.value);
  }
});

function open(modalMode: 'create' | 'edit', initial?: CategoryVM) {
  mode.value = modalMode;
  resetForm();

  if (modalMode === 'edit' && initial) {
    originalCategory.value = initial;
    formData.name = initial.name;
  }

  modal?.show();
}

function close() {
  modal?.hide();
}

function resetForm() {
  formData.name = '';
  originalCategory.value = null;
  validationErrors.name = '';
}

function validate(): boolean {
  let valid = true;
  validationErrors.name = '';

  if (!formData.name.trim()) {
    validationErrors.name = 'Nazwa jest wymagana';
    valid = false;
  } else if (formData.name.trim().length > 30) {
    validationErrors.name = 'Nazwa może zawierać maksymalnie 30 znaków';
    valid = false;
  }

  return valid;
}

async function saveCategory() {
  if (!validate()) return;

  // Check uniqueness async before save
  const unique = await checkNameUnique(formData.name, originalCategory.value?.id);
  if (!unique) {
    validationErrors.name = 'Kategoria o tej nazwie już istnieje';
    return;
  }

  let success = false;
  if (mode.value === 'create') {
    success = await createCategory({ name: formData.name.trim() });
  } else if (mode.value === 'edit' && originalCategory.value) {
    success = await updateCategory(originalCategory.value.id, { name: formData.name.trim() });
  }

  if (success) {
    emit('saved');
    close();
  }
}

// Expose methods
defineExpose({ open });
</script>

<style scoped>
.required::after {
  content: '*';
  color: #dc3545;
  margin-left: 2px;
}
</style> 