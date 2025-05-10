<template>
  <!-- Desktop table -->
  <table class="table table-hover align-middle d-none d-md-table" aria-label="Lista kategorii">
    <thead>
      <tr>
        <th scope="col">Nazwa</th>
        <th scope="col" class="text-center">Domyślna</th>
        <th scope="col" class="text-end">Akcje</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="category in categories" :key="category.id">
        <td>{{ category.name }}</td>
        <td class="text-center">
          <i
            class="bi"
            :class="category.isDefault ? 'bi-star-fill text-warning' : 'bi-dash'"
            aria-hidden="true"
          ></i>
          <span class="visually-hidden">{{ category.isDefault ? 'Domyślna' : '' }}</span>
        </td>
        <td class="text-end">
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary me-2"
            @click="$emit('edit', category.id)"
            aria-label="Edytuj kategorię"
          >
            <i class="bi bi-pencil"></i>
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-danger"
            @click="$emit('delete', category.id)"
            aria-label="Usuń kategorię"
            :disabled="category.isDefault"
            :title="category.isDefault ? 'Nie można usunąć domyślnej kategorii' : 'Usuń'"
          >
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    </tbody>
  </table>

  <!-- Mobile list -->
  <ul class="list-group d-md-none" aria-label="Lista kategorii">
    <li
      v-for="category in categories"
      :key="category.id"
      class="list-group-item d-flex justify-content-between align-items-center"
    >
      <div>
        <span>{{ category.name }}</span>
        <i
          v-if="category.isDefault"
          class="bi bi-star-fill text-warning small ms-1"
          aria-hidden="true"
        ></i>
      </div>
      <div>
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary me-2"
          @click="$emit('edit', category.id)"
          aria-label="Edytuj kategorię"
        >
          <i class="bi bi-pencil"></i>
        </button>
        <button
          type="button"
          class="btn btn-sm btn-outline-danger"
          @click="$emit('delete', category.id)"
          aria-label="Usuń kategorię"
          :disabled="category.isDefault"
        >
          <i class="bi bi-trash"></i>
        </button>
      </div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { CategoryVM } from '../types/categories';

const props = defineProps<{
  categories: CategoryVM[];
}>();
</script>

<style scoped>
/* No additional styles */
</style> 