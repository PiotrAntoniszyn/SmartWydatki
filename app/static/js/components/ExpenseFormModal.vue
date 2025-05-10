<template>
  <div class="modal fade" ref="expenseModal" tabindex="-1" aria-labelledby="expenseModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="expenseModalLabel">
            <i class="bi" :class="isEditMode ? 'bi-pencil' : 'bi-plus-lg'" aria-hidden="true"></i>
            {{ isEditMode ? 'Edytuj wydatek' : 'Dodaj wydatek' }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Zamknij"></button>
        </div>
        <div class="modal-body">
          <form id="expense-form" @submit.prevent="saveExpense">
            <!-- Amount field -->
            <div class="mb-3">
              <label for="expense-amount" class="form-label required">Kwota</label>
              <div class="input-group">
                <input
                  type="number"
                  class="form-control"
                  id="expense-amount"
                  v-model="formData.amount"
                  min="0.01"
                  step="0.01"
                  placeholder="0.00"
                  required
                  aria-describedby="amount-addon"
                  :class="{ 'is-invalid': validationErrors.amount }"
                >
                <span class="input-group-text" id="amount-addon">PLN</span>
                <div class="invalid-feedback" v-if="validationErrors.amount">
                  {{ validationErrors.amount }}
                </div>
              </div>
            </div>
            
            <!-- Description field -->
            <div class="mb-3">
              <label for="expense-description" class="form-label">Opis</label>
              <textarea
                class="form-control"
                id="expense-description"
                v-model="formData.description"
                rows="2"
                maxlength="100"
                placeholder="Opcjonalny opis wydatku"
                :class="{ 'is-invalid': validationErrors.description }"
              ></textarea>
              <div class="form-text text-end">
                {{ formData.description.length }}/100
              </div>
              <div class="invalid-feedback" v-if="validationErrors.description">
                {{ validationErrors.description }}
              </div>
            </div>
            
            <!-- Category field -->
            <div class="mb-3">
              <label for="expense-category" class="form-label required">Kategoria</label>
              <select
                class="form-select"
                id="expense-category"
                v-model="formData.categoryId"
                required
                :class="{ 'is-invalid': validationErrors.categoryId }"
              >
                <option value="" disabled>Wybierz kategorię</option>
                <option 
                  v-for="category in categories" 
                  :key="category.id" 
                  :value="category.id"
                >
                  {{ category.name }}
                </option>
              </select>
              <div class="invalid-feedback" v-if="validationErrors.categoryId">
                {{ validationErrors.categoryId }}
              </div>
            </div>
            
            <!-- Date field - only in edit mode -->
            <div class="mb-3" v-if="isEditMode">
              <label for="expense-date" class="form-label required">Data</label>
              <input
                type="date"
                class="form-control"
                id="expense-date"
                v-model="formData.date"
                required
                :class="{ 'is-invalid': validationErrors.date }"
              >
              <div class="invalid-feedback" v-if="validationErrors.date">
                {{ validationErrors.date }}
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Anuluj
          </button>
          <button type="submit" form="expense-form" class="btn btn-primary">
            <i class="bi bi-save me-1"></i>
            Zapisz
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue';
import type { ExpenseVM, CategoryVM, ExpenseFormData } from '../types/expenses';
import type { Modal as BootstrapModal } from 'bootstrap';

const emit = defineEmits<{
  (e: 'save', expense: ExpenseVM, mode: 'add' | 'edit'): void;
}>();

const props = defineProps<{
  categories: CategoryVM[];
}>();

// Modal reference and instance
const expenseModal = ref<HTMLElement | null>(null);
let modal: BootstrapModal | null = null;

// Form state
const mode = ref<'add' | 'edit'>('add');
const originalExpense = ref<ExpenseVM | null>(null);
const formData = reactive<ExpenseFormData>({
  amount: 0,
  description: '',
  categoryId: '',
  date: new Date().toISOString().split('T')[0]
});

// Validation errors
const validationErrors = reactive({
  amount: '',
  description: '',
  categoryId: '',
  date: '',
});

// Computed properties
const isEditMode = computed(() => mode.value === 'edit');
const modalTitle = computed(() => isEditMode.value ? 'Edytuj wydatek' : 'Dodaj wydatek');

// Initialize modal on mount
onMounted(() => {
  if (expenseModal.value && window.bootstrap) {
    modal = new window.bootstrap.Modal(expenseModal.value);
  }
  
  // Set default category if available
  if (props.categories.length > 0) {
    const defaultCategory = props.categories.find(c => c.isDefault);
    if (defaultCategory) {
      formData.categoryId = defaultCategory.id;
    } else {
      formData.categoryId = props.categories[0].id;
    }
  }
});

// Reset form data
const resetForm = () => {
  formData.amount = 0;
  formData.description = '';
  
  // Set default category if available
  if (props.categories.length > 0) {
    const defaultCategory = props.categories.find(c => c.isDefault);
    if (defaultCategory) {
      formData.categoryId = defaultCategory.id;
    } else {
      formData.categoryId = props.categories[0].id;
    }
  } else {
    formData.categoryId = '';
  }
  
  // Set today's date
  formData.date = new Date().toISOString().split('T')[0];
  
  // Reset validation errors
  Object.keys(validationErrors).forEach(key => {
    validationErrors[key as keyof typeof validationErrors] = '';
  });
};

// Validate form data
const validateForm = (): boolean => {
  let isValid = true;
  
  // Validate amount
  if (!formData.amount || formData.amount <= 0) {
    validationErrors.amount = 'Kwota musi być większa niż 0';
    isValid = false;
  } else if (!/^\d+(\.\d{1,2})?$/.test(formData.amount.toString())) {
    validationErrors.amount = 'Kwota może mieć maksymalnie 2 miejsca po przecinku';
    isValid = false;
  } else {
    validationErrors.amount = '';
  }
  
  // Validate description length
  if (formData.description.length > 100) {
    validationErrors.description = 'Opis nie może być dłuższy niż 100 znaków';
    isValid = false;
  } else {
    validationErrors.description = '';
  }
  
  // Validate category
  if (!formData.categoryId) {
    validationErrors.categoryId = 'Wybierz kategorię';
    isValid = false;
  } else {
    validationErrors.categoryId = '';
  }
  
  // Validate date in edit mode
  if (isEditMode.value && !formData.date) {
    validationErrors.date = 'Data jest wymagana';
    isValid = false;
  } else {
    validationErrors.date = '';
  }
  
  return isValid;
};

// Save expense
const saveExpense = () => {
  if (!validateForm()) {
    return;
  }
  
  // Prepare data for emission, mapping form data to ExpenseVM
  const expenseData: ExpenseVM = {
    id: isEditMode.value && originalExpense.value ? originalExpense.value.id : crypto.randomUUID(),
    amount: Number(formData.amount),
    description: formData.description,
    categoryId: formData.categoryId,
    // Format date for display 'DD/MM/YYYY'
    date: new Date(formData.date).toLocaleDateString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }),
    // ISO format for API
    datetime: new Date(formData.date).toISOString(),
    // Use current date as created date for new expenses
    createdAt: isEditMode.value && originalExpense.value 
      ? originalExpense.value.createdAt 
      : new Date().toISOString(),
    // Add category name from selected category
    categoryName: props.categories.find(c => c.id === formData.categoryId)?.name || ''
  };
  
  emit('save', expenseData, mode.value);
  closeModal();
};

// Open modal in add or edit mode
const open = (openMode: 'add' | 'edit', expense?: ExpenseVM) => {
  mode.value = openMode;
  
  if (openMode === 'edit' && expense) {
    originalExpense.value = expense;
    
    // Fill form with expense data
    formData.amount = expense.amount;
    formData.description = expense.description;
    formData.categoryId = expense.categoryId;
    
    // Convert date from display format to ISO date for input
    const dateParts = expense.date.split('/');
    if (dateParts.length === 3) {
      const day = parseInt(dateParts[0]);
      const month = parseInt(dateParts[1]) - 1; // JS months are 0-indexed
      const year = parseInt(dateParts[2]);
      formData.date = new Date(year, month, day).toISOString().split('T')[0];
    } else {
      // Fallback if date format is not as expected
      formData.date = new Date().toISOString().split('T')[0];
    }
  } else {
    resetForm();
    originalExpense.value = null;
  }
  
  // Reset validation errors
  Object.keys(validationErrors).forEach(key => {
    validationErrors[key as keyof typeof validationErrors] = '';
  });
  
  modal?.show();
};

// Close modal
const closeModal = () => {
  modal?.hide();
};

// Expose methods to parent
defineExpose({
  open
});
</script>

<style scoped>
.required::after {
  content: '*';
  color: var(--bs-danger);
  margin-left: 0.25rem;
}

.form-text {
  font-size: 0.75rem;
  color: #6c757d;
}
</style> 