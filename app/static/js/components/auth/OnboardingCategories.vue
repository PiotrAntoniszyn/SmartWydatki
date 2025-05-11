<template>
  <div class="onboarding-container">
    <div class="onboarding-content">
      <h2 class="text-center mb-2">Rozpocznij korzystanie z aplikacji</h2>
      <p class="text-center mb-4">Wybierz kategorie wydatków, które chcesz śledzić</p>
      
      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Ładowanie...</span>
        </div>
        <p class="mt-3">Ładowanie kategorii...</p>
      </div>
      
      <div v-else-if="error" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <div class="mt-3">
          <button class="btn btn-outline-danger" @click="loadCategories">
            <i class="bi bi-arrow-clockwise me-1"></i> Spróbuj ponownie
          </button>
        </div>
      </div>
      
      <div v-else>
        <div class="categories-list mb-4">
          <div 
            v-for="category in categories" 
            :key="category.id"
            class="category-item"
            :class="{ 'selected': selectedCategories.includes(category.id) }"
            @click="toggleCategory(category.id)"
          >
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                :id="`category-${category.id}`"
                :value="category.id"
                v-model="selectedCategories"
              >
              <label class="form-check-label" :for="`category-${category.id}`">
                {{ category.name }}
              </label>
            </div>
          </div>
        </div>
        
        <div v-if="validationError" class="alert alert-danger mb-4" role="alert">
          {{ validationError }}
        </div>
        
        <div class="d-flex justify-content-between">
          <button 
            type="button" 
            class="btn btn-link"
            @click="skipOnboarding"
          >
            Pomiń ten krok
          </button>
          
          <button 
            type="button" 
            class="btn btn-primary"
            :disabled="savingCategories"
            @click="saveSelectedCategories"
          >
            <span v-if="savingCategories" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Rozpocznij
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Category {
  id: string;
  name: string;
}

// State
const categories = ref<Category[]>([]);
const selectedCategories = ref<string[]>([]);
const loading = ref(true);
const savingCategories = ref(false);
const error = ref('');
const validationError = ref('');

// Sample categories data (would normally come from API)
const sampleCategories: Category[] = [
  { id: '1', name: 'Mieszkanie' },
  { id: '2', name: 'Jedzenie' },
  { id: '3', name: 'Transport' },
  { id: '4', name: 'Rozrywka' },
  { id: '5', name: 'Zdrowie' },
  { id: '6', name: 'Podróże' },
  { id: '7', name: 'Edukacja' },
  { id: '8', name: 'Ubrania' },
  { id: '9', name: 'Hobby' },
  { id: '10', name: 'Inne' }
];

// Load categories on mount
onMounted(() => {
  loadCategories();
});

async function loadCategories() {
  loading.value = true;
  error.value = '';
  
  try {
    // Here we would call the API to get suggested categories
    // For now we'll use the sample data
    await new Promise(resolve => setTimeout(resolve, 800)); // Simulate API delay
    
    categories.value = sampleCategories;
  } catch (err) {
    error.value = 'Nie udało się załadować sugerowanych kategorii. Spróbuj ponownie.';
  } finally {
    loading.value = false;
  }
}

function toggleCategory(categoryId: string) {
  const index = selectedCategories.value.indexOf(categoryId);
  if (index === -1) {
    selectedCategories.value.push(categoryId);
  } else {
    selectedCategories.value.splice(index, 1);
  }
}

async function saveSelectedCategories() {
  validationError.value = '';
  
  if (selectedCategories.value.length === 0) {
    validationError.value = 'Wybierz co najmniej jedną kategorię.';
    return;
  }
  
  savingCategories.value = true;
  
  try {
    // Here we would call the API to save selected categories
    // For now we're just simulating the API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Redirect to dashboard after successful save
    console.log('Selected categories saved:', selectedCategories.value);
    
    // Redirect would happen here
    // router.push('/dashboard');
    
  } catch (err) {
    validationError.value = 'Nie udało się zapisać wybranych kategorii. Spróbuj ponownie.';
  } finally {
    savingCategories.value = false;
  }
}

function skipOnboarding() {
  // Redirect to dashboard without saving categories
  console.log('Onboarding skipped');
  
  // Redirect would happen here
  // router.push('/dashboard');
}
</script>

<style scoped>
.onboarding-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.onboarding-content {
  max-width: 500px;
  width: 100%;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  background-color: #fff;
}

.categories-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
}

.category-item {
  padding: 0.75rem;
  border-radius: 0.25rem;
  border: 1px solid #dee2e6;
  transition: all 0.2s ease;
  cursor: pointer;
}

.category-item:hover {
  border-color: #adb5bd;
  background-color: #f8f9fa;
}

.category-item.selected {
  border-color: #0d6efd;
  background-color: #f0f7ff;
}

.category-item .form-check {
  margin-bottom: 0;
}
</style> 