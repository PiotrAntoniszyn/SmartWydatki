<template>
  <div class="auth-form">
    <h2 class="text-center mb-4">Logowanie</h2>
    
    <form @submit.prevent="handleLogin">
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
            placeholder="Twoje hasło"
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
      </div>

      <!-- Remember me checkbox -->
      <div class="mb-3 form-check">
        <input 
          type="checkbox" 
          class="form-check-input" 
          id="remember-me"
          v-model="formData.rememberMe" 
        />
        <label class="form-check-label" for="remember-me">Zapamiętaj mnie</label>
      </div>

      <!-- Forgot password link -->
      <div class="mb-3 text-end">
        <router-link to="/reset-password" class="text-decoration-none">Nie pamiętasz hasła?</router-link>
      </div>

      <!-- Login button -->
      <div class="d-grid gap-2">
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Zaloguj się
        </button>
      </div>

      <!-- Register link -->
      <div class="mt-3 text-center">
        Nie masz konta? <router-link to="/register" class="text-decoration-none">Zarejestruj się</router-link>
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
  rememberMe: false
});

const validationErrors = reactive({
  email: '',
  password: '',
  general: ''
});

const isLoading = ref(false);
const showPassword = ref(false);

// Toggle password visibility
function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
}

// Form validation
function validate(): boolean {
  let isValid = true;
  
  // Reset errors
  validationErrors.email = '';
  validationErrors.password = '';
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
  }

  return isValid;
}

// Handle login form submission
async function handleLogin() {
  if (!validate()) return;
  
  isLoading.value = true;
  
  try {
    // Here we would call the login API
    // For now we're just simulating the UI behavior
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // For UI purposes, we'll just redirect to /dashboard
    // This would normally happen after successful login
    console.log('Login successful');
    
  } catch (error) {
    // Handle API errors
    validationErrors.general = 'Nieprawidłowy email lub hasło';
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