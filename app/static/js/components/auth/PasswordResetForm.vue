<template>
  <div class="auth-form">
    <h2 class="text-center mb-4">Resetowanie hasła</h2>
    
    <div v-if="!emailSent">
      <p class="text-center mb-4">Podaj adres email powiązany z Twoim kontem, a my wyślemy Ci link do resetowania hasła.</p>
      
      <form @submit.prevent="handleResetRequest">
        <!-- Email field -->
        <div class="mb-3">
          <label for="email" class="form-label required">Email</label>
          <input
            type="email"
            class="form-control"
            id="email"
            v-model="formData.email"
            required
            placeholder="twoj@email.com"
            :class="{ 'is-invalid': validationErrors.email }"
          />
          <div class="invalid-feedback" v-if="validationErrors.email">
            {{ validationErrors.email }}
          </div>
        </div>

        <!-- Reset button -->
        <div class="d-grid gap-2">
          <button 
            type="submit" 
            class="btn btn-primary"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Wyślij link resetujący
          </button>
        </div>

        <!-- Login link -->
        <div class="mt-3 text-center">
          <router-link to="/login" class="text-decoration-none">Powrót do logowania</router-link>
        </div>
      </form>
    </div>

    <div v-else class="text-center">
      <div class="mb-4">
        <i class="bi bi-check-circle text-success" style="font-size: 3rem;"></i>
      </div>
      
      <h4 class="mb-3">Email został wysłany!</h4>
      
      <p>Na adres <strong>{{ formData.email }}</strong> wysłaliśmy link do resetowania hasła.</p>
      <p class="mb-4">Sprawdź swoją skrzynkę i kliknij na przesłany link aby ustawić nowe hasło.</p>
      
      <button 
        type="button" 
        class="btn btn-primary"
        @click="resetForm"
      >
        Spróbuj ponownie
      </button>
      
      <div class="mt-3">
        <router-link to="/login" class="text-decoration-none">Powrót do logowania</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useApi } from '../../composables/useApi';

// State
const formData = reactive({
  email: ''
});

const validationErrors = reactive({
  email: '',
  general: ''
});

const isLoading = ref(false);
const emailSent = ref(false);
const api = useApi();

// Form validation
function validate(): boolean {
  let isValid = true;
  
  // Reset errors
  validationErrors.email = '';
  validationErrors.general = '';

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!formData.email) {
    validationErrors.email = 'Email jest wymagany';
    isValid = false;
  } else if (!emailRegex.test(formData.email)) {
    validationErrors.email = 'Nieprawidłowy format email';
    isValid = false;
  }

  return isValid;
}

// Handle reset request form submission
async function handleResetRequest() {
  if (!validate()) return;
  
  isLoading.value = true;
  
  try {
    await api.post('/auth/password/reset-request', { email: formData.email });
    emailSent.value = true;
  } catch (err: any) {
    if (err.field === 'email') {
      validationErrors.email = err.error;
    } else {
      validationErrors.general = typeof err === 'string' ? err : 'Nie udało się wysłać linku resetującego. Spróbuj ponownie.';
    }
  } finally {
    isLoading.value = false;
  }
}

// Reset form to initial state
function resetForm() {
  formData.email = '';
  emailSent.value = false;
  validationErrors.email = '';
  validationErrors.general = '';
}
</script>

<style scoped>
.auth-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  background-color: #fff;
}

.required::after {
  content: '*';
  color: #dc3545;
  margin-left: 2px;
}
</style> 