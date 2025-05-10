<template>
  <div id="expenses-app" class="expenses-container">
    <h1>Lista wydatków</h1>
    
    <!-- Main content container -->
    <div class="content-container">
      <!-- Empty state when no expenses -->
      <div v-if="!loading && expenses.length === 0" class="empty-state">
        <p>Lista jest pusta</p>
        <button 
          type="button" 
          id="add-expense" 
          class="btn btn-primary" 
          @click="openAddExpenseModal"
        >
          Dodaj wydatek
        </button>
      </div>
      
      <!-- Filter panel button -->
      <div class="action-buttons mb-3">
        <button 
          type="button" 
          class="btn btn-outline-secondary me-2" 
          @click="openFilterModal"
        >
          <i class="bi bi-funnel"></i> Filtruj
        </button>
        <button 
          type="button" 
          class="btn btn-primary" 
          @click="openAddExpenseModal"
        >
          <i class="bi bi-plus"></i> Dodaj wydatek
        </button>
      </div>
      
      <!-- Expenses table -->
      <ExpensesTable 
        v-if="!loading && expenses.length > 0" 
        :expenses="expenses"
        @edit="openEditExpenseModal"
        @delete="openDeleteConfirmModal"
      />
      
      <!-- Pagination controls -->
      <PaginationControls 
        v-if="!loading && expenses.length > 0" 
        :pagination="pagination"
        @change-page="changePage"
      />
    </div>
    
    <!-- Modals -->
    <FilterPanelModal
      ref="filterModalRef"
      :initial-filters="filterParams"
      @apply-filters="applyFilters"
      @reset-filters="resetFilters"
    />
    
    <ExpenseFormModal
      ref="expenseFormModalRef"
      :categories="categories"
      @save="saveExpense"
    />
    
    <ConfirmDialog
      ref="deleteConfirmRef"
      title="Usunąć wydatek?"
      message="Czy na pewno chcesz usunąć ten wydatek? Tej operacji nie można cofnąć."
      confirm-button-text="Usuń"
      @confirm="deleteExpense"
    />
    
    <ErrorDialog
      ref="errorDialogRef"
      @retry="retryFetch"
    />
    
    <!-- Loading spinner -->
    <LoadingSpinner v-if="loading" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useApi } from '../composables/useApi';
import ExpensesTable from '../components/ExpensesTable.vue';
import FilterPanelModal from '../components/FilterPanelModal.vue';
import ExpenseFormModal from '../components/ExpenseFormModal.vue';
import PaginationControls from '../components/PaginationControls.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import ErrorDialog from '../components/ErrorDialog.vue';
import { 
  mapExpensesToViewModels, 
  mapCategoriesToViewModels,
  mapViewModelToExpenseDTO
} from '../utils/expenseMapper';
import type { 
  ExpenseVM, 
  FilterParams,
  PaginationVM,
  CategoryVM
} from '../types/expenses';

// API client
const api = useApi();

// Component refs
const filterModalRef = ref<InstanceType<typeof FilterPanelModal> | null>(null);
const expenseFormModalRef = ref<InstanceType<typeof ExpenseFormModal> | null>(null);
const deleteConfirmRef = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const errorDialogRef = ref<InstanceType<typeof ErrorDialog> | null>(null);

// State
const expenses = ref<ExpenseVM[]>([]);
const categories = ref<CategoryVM[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const selectedExpenseId = ref<string | null>(null);

// Pagination state
const pagination = reactive<PaginationVM>({
  limit: 20,
  offset: 0,
  total: 0,
  currentPage: 1,
  totalPages: 1
});

// Filter state
const filterParams = reactive<FilterParams>({
  search: '',
  dateFrom: null,
  dateTo: null,
  amountMin: null,
  amountMax: null
});

// Fetch expenses with current filters and pagination
const fetchExpenses = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.get('/expenses', {
      params: {
        ...filterParams,
        limit: pagination.limit,
        offset: pagination.offset
      }
    });
    
    const responseData = response.data;
    expenses.value = mapExpensesToViewModels(responseData.data, categories.value);
    
    // Update pagination info
    pagination.total = responseData.pagination.total;
    pagination.totalPages = Math.ceil(responseData.pagination.total / pagination.limit);
    pagination.currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
    
    loading.value = false;
  } catch (err) {
    loading.value = false;
    error.value = "Nie udało się załadować wydatków";
    errorDialogRef.value?.open(error.value);
  }
};

// Fetch categories for dropdown in expense form
const fetchCategories = async () => {
  try {
    const response = await api.get('/categories');
    categories.value = mapCategoriesToViewModels(response.data);
  } catch (err) {
    error.value = "Nie udało się załadować kategorii";
    errorDialogRef.value?.open(error.value);
  }
};

// Modal handlers
const openFilterModal = () => {
  filterModalRef.value?.open();
};

const openAddExpenseModal = () => {
  expenseFormModalRef.value?.open('add');
};

const openEditExpenseModal = (expenseId: string) => {
  const expense = expenses.value.find(e => e.id === expenseId);
  if (expense) {
    expenseFormModalRef.value?.open('edit', expense);
  }
};

const openDeleteConfirmModal = (expenseId: string) => {
  selectedExpenseId.value = expenseId;
  deleteConfirmRef.value?.open();
};

// Action handlers
const applyFilters = (filters: FilterParams) => {
  Object.assign(filterParams, filters);
  pagination.offset = 0; // Reset to first page
  fetchExpenses();
};

const resetFilters = () => {
  filterParams.search = '';
  filterParams.dateFrom = null;
  filterParams.dateTo = null;
  filterParams.amountMin = null;
  filterParams.amountMax = null;
  pagination.offset = 0; // Reset to first page
  fetchExpenses();
};

const changePage = (newOffset: number) => {
  pagination.offset = newOffset;
  fetchExpenses();
};

const saveExpense = async (expense: ExpenseVM, mode: 'add' | 'edit') => {
  loading.value = true;
  
  try {
    const expenseDTO = mapViewModelToExpenseDTO(expense);
    
    if (mode === 'add') {
      await api.post('/expenses', expenseDTO);
    } else {
      await api.put(`/expenses/${expense.id}`, expenseDTO);
    }
    
    fetchExpenses(); // Refresh the list
  } catch (err) {
    loading.value = false;
    error.value = mode === 'add' 
      ? "Nie udało się dodać wydatku" 
      : "Nie udało się zaktualizować wydatku";
    errorDialogRef.value?.open(error.value);
  }
};

const deleteExpense = async () => {
  if (!selectedExpenseId.value) return;
  
  loading.value = true;
  
  try {
    await api.delete(`/expenses/${selectedExpenseId.value}`);
    fetchExpenses(); // Refresh the list
  } catch (err) {
    loading.value = false;
    error.value = "Nie udało się usunąć wydatku";
    errorDialogRef.value?.open(error.value);
  }
};

const retryFetch = () => {
  fetchExpenses();
  fetchCategories();
};

// Lifecycle hooks
onMounted(() => {
  fetchExpenses();
  fetchCategories();
});
</script>

<style scoped>
.expenses-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.content-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-top: 1rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
}

@media (max-width: 768px) {
  .content-container {
    padding: 1rem;
  }
}
</style> 