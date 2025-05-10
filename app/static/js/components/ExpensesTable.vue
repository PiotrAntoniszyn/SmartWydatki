<template>
  <div class="table-responsive">
    <table class="table table-hover">
      <thead>
        <tr>
          <th scope="col" class="date-col">Data</th>
          <th scope="col" class="flex-grow-1">Opis</th>
          <th scope="col" class="category-col">Kategoria</th>
          <th scope="col" class="amount-col">Kwota</th>
          <th scope="col" class="actions-col">Akcje</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="expense in expenses" :key="expense.id">
          <td class="date-col">{{ formatDate(expense.date) }}</td>
          <td class="description-col">
            {{ expense.description || '(brak opisu)' }}
          </td>
          <td class="category-col">{{ expense.categoryName }}</td>
          <td class="amount-col">{{ formatAmount(expense.amount) }}</td>
          <td class="actions-col">
            <div class="d-flex gap-2">
              <button 
                type="button" 
                class="btn btn-sm btn-outline-secondary"
                title="Edytuj"
                aria-label="Edytuj wydatek"
                @click="$emit('edit', expense.id)"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button 
                type="button" 
                class="btn btn-sm btn-outline-danger"
                title="Usuń"
                aria-label="Usuń wydatek"
                @click="$emit('delete', expense.id)"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import type { ExpenseVM } from '../types/expenses';

defineEmits<{
  (e: 'edit', id: string): void
  (e: 'delete', id: string): void
}>();

const props = defineProps<{
  expenses: ExpenseVM[]
}>();

// Format date from ISO to DD/MM/YYYY
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

// Format amount with currency
const formatAmount = (amount: number): string => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};
</script>

<style scoped>
.table {
  table-layout: fixed;
  width: 100%;
}

.date-col {
  width: 100px;
}

.category-col {
  width: 120px;
}

.amount-col {
  width: 120px;
  text-align: right;
}

.actions-col {
  width: 100px;
  text-align: center;
}

.description-col {
  word-break: break-word;
}

@media (max-width: 768px) {
  .date-col {
    width: 80px;
  }
  
  .category-col {
    width: 100px;
  }
}
</style> 