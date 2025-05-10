<template>
  <div class="container mt-4" id="categories-page">
    <h1>Zarządzanie kategoriami</h1>

    <!-- Action toolbar -->
    <div class="d-flex justify-content-end mb-3">
      <button
        type="button"
        class="btn btn-primary"
        aria-label="Dodaj kategorię"
        @click="openAddCategoryModal"
      >
        <i class="bi bi-plus-lg" aria-hidden="true"></i>
        <span class="ms-1">Dodaj kategorię</span>
      </button>
    </div>

    <!-- Loading spinner -->
    <LoadingSpinner v-if="loading" />

    <!-- Empty state -->
    <div v-if="!loading && categories.length === 0 && !error" class="alert alert-info" role="alert">
      Lista kategorii jest pusta.
      <button type="button" class="btn btn-primary ms-2" @click="openAddCategoryModal">Dodaj kategorię</button>
    </div>

    <!-- Categories list component -->
    <CategoriesList
      v-if="!loading && categories.length > 0"
      :categories="categories"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <!-- Modals -->
    <CategoryFormModal ref="categoryFormModalRef" @saved="fetchCategories" />
    <DeleteCategoryConfirmDialog
      ref="deleteConfirmRef"
      title="Usunąć kategorię?"
      message="Czy na pewno chcesz usunąć tę kategorię? Tej operacji nie można cofnąć."
      confirm-button-text="Usuń"
      @confirm="deleteCategory"
    />

    <ErrorDialog ref="errorDialogRef" @retry="fetchCategories" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useCategories } from '../composables/useCategories';
import CategoryFormModal from '../components/CategoryFormModal.vue';
import DeleteCategoryConfirmDialog from '../components/DeleteCategoryConfirmDialog.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import ErrorDialog from '../components/ErrorDialog.vue';
import type { CategoryVM } from '../types/categories';
import CategoriesList from '../components/CategoriesList.vue';

// Composable
const {
  categories,
  loading,
  error,
  fetch: fetchCategories,
  remove: removeCategory
} = useCategories();

// Component refs
const categoryFormModalRef = ref<InstanceType<typeof CategoryFormModal> | null>(null);
const deleteConfirmRef = ref<InstanceType<typeof DeleteCategoryConfirmDialog> | null>(null);
const errorDialogRef = ref<InstanceType<typeof ErrorDialog> | null>(null);

// Selected category for deletion
const selectedCategory = ref<CategoryVM | null>(null);

// Fetch categories on mount
onMounted(async () => {
  await fetchCategories();
});

// Watch for error changes and open dialog
watch(error, (val) => {
  if (val) {
    errorDialogRef.value?.open(val as string);
  }
});

function openAddCategoryModal() {
  categoryFormModalRef.value?.open('create');
}

function openEditCategoryModal(category: CategoryVM) {
  categoryFormModalRef.value?.open('edit', category);
}

function openDeleteConfirm(category: CategoryVM) {
  selectedCategory.value = category;
  deleteConfirmRef.value?.open();
}

async function deleteCategory() {
  if (!selectedCategory.value) return;
  const success = await removeCategory(selectedCategory.value.id);
  if (success) {
    await fetchCategories();
  }
}

function handleEdit(id: string) {
  const category = categories.value.find(c => c.id === id);
  if (category) {
    openEditCategoryModal(category);
  }
}

function handleDelete(id: string) {
  const category = categories.value.find(c => c.id === id);
  if (category) {
    openDeleteConfirm(category);
  }
}
</script>

<style scoped>
/* Custom styles can be added here */
</style> 