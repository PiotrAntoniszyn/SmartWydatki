<template>
  <div class="auth-form">
    <h2 class="text-center mb-4">Rejestracja</h2>
    
    <form @submit.prevent="handleRegister">
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

      <!-- Password field -->
      <div class="mb-3">
        <label for="password" class="form-label required">Hasło</label>
        <div class="input-group">
          <input
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            id="password"
            v-model="formData.password"
            required
            placeholder="Minimum 8 znaków"
            :class="{ 'is-invalid': validationErrors.password }"
          />
          <button 
            class="btn btn-outline-secondary" 
            type="button"
            @click="togglePasswordVisibility"
          >
            <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
          </button>
          <div class="invalid-feedback" v-if="validationErrors.password">
            {{ validationErrors.password }}
          </div>
        </div>
        <div class="form-text">Hasło musi mieć co najmniej 8 znaków.</div>
      </div>

      <!-- Confirm Password field -->
      <div class="mb-3">
        <label for="confirm-password" class="form-label required">Potwierdź hasło</label>
        <div class="input-group">
          <input
            :type="showConfirmPassword ? 'text' : 'password'"
            class="form-control"
            id="confirm-password"
            v-model="formData.passwordConfirm"
            required
            placeholder="Powtórz hasło"
            :class="{ 'is-invalid': validationErrors.passwordConfirm }"
          />
          <button 
            class="btn btn-outline-secondary" 
            type="button"
            @click="toggleConfirmPasswordVisibility"
          >
            <i class="bi" :class="showConfirmPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
          </button>
          <div class="invalid-feedback" v-if="validationErrors.passwordConfirm">
            {{ validationErrors.passwordConfirm }}
          </div>
        </div>
      </div>

      <!-- Terms and Conditions -->
      <div class="mb-3 form-check">
        <input 
          type="checkbox" 
          class="form-check-input" 
          id="terms"
          v-model="formData.termsAccepted"
          :class="{ 'is-invalid': validationErrors.termsAccepted }"
        />
        <label class="form-check-label" for="terms">
          Akceptuję <a href="#" class="text-decoration-none">regulamin</a> i <a href="#" class="text-decoration-none">politykę prywatności</a>
        </label>
        <div class="invalid-feedback" v-if="validationErrors.termsAccepted">
          {{ validationErrors.termsAccepted }}
        </div>
      </div>

      <!-- Register button -->
      <div class="d-grid gap-2">
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Zarejestruj się
        </button>
      </div>

      <!-- Login link -->
      <div class="mt-3 text-center">
        Masz już konto? <router-link to="/login" class="text-decoration-none">Zaloguj się</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

// State
const formData = reactive({
  email: '',
  password: '',
  passwordConfirm: '',
  termsAccepted: false
});

const validationErrors = reactive({
  email: '',
  password: '',
  passwordConfirm: '',
  termsAccepted: '',
  general: ''
});

const isLoading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);

// Toggle password visibility
function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
}

function toggleConfirmPasswordVisibility() {
  showConfirmPassword.value = !showConfirmPassword.value;
}

// Form validation
function validate(): boolean {
  let isValid = true;
  
  // Reset errors
  validationErrors.email = '';
  validationErrors.password = '';
  validationErrors.passwordConfirm = '';
  validationErrors.termsAccepted = '';
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

  // Password validation
  if (!formData.password) {
    validationErrors.password = 'Hasło jest wymagane';
    isValid = false;
  } else if (formData.password.length < 8) {
    validationErrors.password = 'Hasło musi mieć co najmniej 8 znaków';
    isValid = false;
  }

  // Password confirmation validation
  if (!formData.passwordConfirm) {
    validationErrors.passwordConfirm = 'Potwierdzenie hasła jest wymagane';
    isValid = false;
  } else if (formData.password !== formData.passwordConfirm) {
    validationErrors.passwordConfirm = 'Hasła nie są identyczne';
    isValid = false;
  }

  // Terms acceptance validation
  if (!formData.termsAccepted) {
    validationErrors.termsAccepted = 'Musisz zaakceptować regulamin i politykę prywatności';
    isValid = false;
  }

  return isValid;
}

// Handle register form submission
async function handleRegister() {
  if (!validate()) return;
  
  isLoading.value = true;
  
  try {
    // Here we would call the registration API
    // For now we're just simulating the UI behavior
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // For UI purposes, we'll just redirect to /onboarding
    // This would normally happen after successful registration
    console.log('Registration successful');
    
  } catch (error) {
    // Handle API errors
    validationErrors.general = 'Nie udało się zarejestrować konta. Spróbuj ponownie.';
    
    // Handling specific API errors like email already in use
    if (error.message === 'Email already exists') {
      validationErrors.email = 'E-mail jest już używany';
    }
  } finally {
    isLoading.value = false;
  }
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