<template>
  <v-dialog
    v-model="dialog"
    persistent
    fullscreen
    no-click-animation
    :retain-focus="false"
    :scrim="false"
    transition="fade-transition"
    role="dialog"
    aria-modal="true"
    aria-labelledby="onboarding-title"
  >
    <v-card class="d-flex flex-column" style="min-height: 100vh;">
      <v-card-title id="onboarding-title" class="text-h4 text-center pa-6">
        Witaj w aplikacji!
      </v-card-title>
      
      <v-card-text class="flex-grow-1 d-flex flex-column align-center justify-center">
        <!-- Loading state -->
        <LoadingSpinner v-if="loading" />
        
        <!-- Error state -->
        <ErrorDialog 
          :message="errorMessage"
          @retry="fetchSuggestions"
        />
        
        <!-- Content -->
        <div v-if="!loading && !errorMessage" class="onboarding-content">
          <CategoriesSuggestionsList
            :items="suggestions"
            v-model:selectedIds="selectedIds"
          />
        </div>
      </v-card-text>
      
      <v-card-actions class="justify-center pa-6">
        <v-btn
          color="primary"
          size="large"
          min-width="200"
          :disabled="!canContinue"
          @click="handleContinue"
          aria-label="Kontynuuj do aplikacji"
        >
          Kontynuuj
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import ErrorDialog from '../components/ErrorDialog.vue';
import CategoriesSuggestionsList from '../components/CategoriesSuggestionsList.vue';
import { useApi } from '../composables/useApi';
import { useOnboardingSuggestions } from '../composables/useOnboardingSuggestions';

const router = useRouter();
const dialog = ref(true);
const api = useApi();

// Get onboarding suggestions state and methods from composable
const {
  suggestions,
  loading,
  errorMessage,
  selectedIds,
  fetchSuggestions,
  canContinue
} = useOnboardingSuggestions();

// Fetch suggestions when component is mounted
onMounted(() => {
  fetchSuggestions();
});

// Handle continue button click
const handleContinue = async () => {
  // Save selected categories via API
  try {
    await api.post('/categories/initial', { categoryIds: selectedIds.value });
    router.push('/dashboard');
  } catch (err) {
    // Display error in dialog
    errorMessage.value = 'Nie udało się zapisać wybranych kategorii. Spróbuj ponownie.';
  }
};
</script>

<style scoped>
.onboarding-content {
  width: 100%;
  max-width: 800px;
  padding: 2rem;
}

/* Ensure the dialog takes the full screen on mobile */
@media (max-width: 600px) {
  .onboarding-content {
    padding: 1rem;
  }
}
</style> 