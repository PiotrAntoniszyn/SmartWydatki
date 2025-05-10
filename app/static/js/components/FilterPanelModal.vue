<template>
  <div class="modal fade" ref="filterModal" tabindex="-1" aria-labelledby="filterModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="filterModalLabel">
            <i class="bi bi-funnel me-2"></i>
            Filtry wydatków
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Zamknij"></button>
        </div>
        <div class="modal-body">
          <form id="filter-form" @submit.prevent="applyFilters">
            <!-- Search input -->
            <div class="mb-3">
              <label for="filter-search" class="form-label">Szukaj w opisie</label>
              <input 
                type="text" 
                class="form-control" 
                id="filter-search" 
                v-model="filters.search"
                placeholder="Wpisz tekst do wyszukania"
              >
            </div>
            
            <!-- Date range -->
            <div class="row mb-3">
              <div class="col-md-6">
                <label for="filter-date-from" class="form-label">Data od</label>
                <input 
                  type="date" 
                  class="form-control" 
                  id="filter-date-from" 
                  v-model="filters.dateFrom"
                >
              </div>
              <div class="col-md-6">
                <label for="filter-date-to" class="form-label">Data do</label>
                <input 
                  type="date" 
                  class="form-control" 
                  id="filter-date-to" 
                  v-model="filters.dateTo"
                >
                <div v-if="dateError" class="invalid-feedback d-block">
                  {{ dateError }}
                </div>
              </div>
            </div>
            
            <!-- Amount range -->
            <div class="row mb-3">
              <div class="col-md-6">
                <label for="filter-amount-min" class="form-label">Kwota od</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="filter-amount-min" 
                  min="0" 
                  step="0.01" 
                  v-model="filters.amountMin"
                  placeholder="Min"
                >
              </div>
              <div class="col-md-6">
                <label for="filter-amount-max" class="form-label">Kwota do</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="filter-amount-max" 
                  min="0" 
                  step="0.01" 
                  v-model="filters.amountMax"
                  placeholder="Max"
                >
                <div v-if="amountError" class="invalid-feedback d-block">
                  {{ amountError }}
                </div>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-outline-secondary" 
            @click="resetFilters"
          >
            <i class="bi bi-arrow-counterclockwise me-1"></i>
            Resetuj
          </button>
          <button 
            type="submit" 
            form="filter-form" 
            class="btn btn-primary"
          >
            <i class="bi bi-check-lg me-1"></i>
            Zastosuj
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue';
import type { FilterParams } from '../types/expenses';
import type { Modal as BootstrapModal } from 'bootstrap';

const emit = defineEmits<{
  (e: 'apply-filters', filters: FilterParams): void;
  (e: 'reset-filters'): void;
}>();

const props = defineProps<{
  initialFilters: FilterParams;
}>();

// Modal reference and instance
const filterModal = ref<HTMLElement | null>(null);
let modal: BootstrapModal | null = null;

// Local filters state as a copy of initialFilters
const filters = reactive<FilterParams>({
  search: '',
  dateFrom: null,
  dateTo: null,
  amountMin: null,
  amountMax: null
});

// Validation errors
const dateError = ref<string | null>(null);
const amountError = ref<string | null>(null);

// Copy initialFilters on component mount
onMounted(() => {
  resetFiltersToInitial();
  
  // Initialize Bootstrap modal
  if (filterModal.value && window.bootstrap) {
    modal = new window.bootstrap.Modal(filterModal.value);
  }
});

// Reset to initial values from props
const resetFiltersToInitial = () => {
  filters.search = props.initialFilters.search || '';
  filters.dateFrom = props.initialFilters.dateFrom;
  filters.dateTo = props.initialFilters.dateTo;
  filters.amountMin = props.initialFilters.amountMin;
  filters.amountMax = props.initialFilters.amountMax;
};

// Watch for date range to validate
watch([() => filters.dateFrom, () => filters.dateTo], () => {
  validateDateRange();
});

// Watch for amount range to validate
watch([() => filters.amountMin, () => filters.amountMax], () => {
  validateAmountRange();
});

// Validate date range
const validateDateRange = (): boolean => {
  dateError.value = null;
  
  if (filters.dateFrom && filters.dateTo) {
    const fromDate = new Date(filters.dateFrom);
    const toDate = new Date(filters.dateTo);
    
    if (fromDate > toDate) {
      dateError.value = 'Data "od" nie może być późniejsza niż data "do"';
      return false;
    }
  }
  
  return true;
};

// Validate amount range
const validateAmountRange = (): boolean => {
  amountError.value = null;
  
  if (filters.amountMin !== null && filters.amountMin < 0) {
    amountError.value = 'Kwota minimalna nie może być ujemna';
    return false;
  }
  
  if (filters.amountMin !== null && filters.amountMax !== null && 
      Number(filters.amountMin) > Number(filters.amountMax)) {
    amountError.value = 'Kwota "od" nie może być większa niż kwota "do"';
    return false;
  }
  
  return true;
};

// Apply filters if valid
const applyFilters = () => {
  const dateValid = validateDateRange();
  const amountValid = validateAmountRange();
  
  if (dateValid && amountValid) {
    emit('apply-filters', { ...filters });
    closeModal();
  }
};

// Reset all filters
const resetFilters = () => {
  filters.search = '';
  filters.dateFrom = null;
  filters.dateTo = null;
  filters.amountMin = null;
  filters.amountMax = null;
  
  dateError.value = null;
  amountError.value = null;
  
  emit('reset-filters');
  closeModal();
};

// Open filter modal
const open = () => {
  resetFiltersToInitial();
  dateError.value = null;
  amountError.value = null;
  modal?.show();
};

// Close filter modal
const closeModal = () => {
  modal?.hide();
};

// Expose methods to parent
defineExpose({
  open
});
</script>

<style scoped>
.invalid-feedback {
  font-size: 80%;
}
</style> 