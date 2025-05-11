<template>
  <div class="auth-form">
    <h2 class="text-center mb-4">Ustaw nowe hasło</h2>
    
    <div v-if="!passwordChanged">
      <p class="text-center mb-4">Wprowadź nowe hasło dla swojego konta.</p>
      
      <form @submit.prevent="handlePasswordChange">
        <!-- Password field -->
        <div class="mb-3">
          <label for="password" class="form-label required">Nowe hasło</label>
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

        <!-- Submit button -->
        <div class="d-grid gap-2">
          <button 
            type="submit" 
            class="btn btn-primary"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Zmień hasło
          </button>
        </div>
      </form>
    </div>

    <div v-else class="text-center">
      <div class="mb-4">
        <i class="bi bi-check-circle text-success" style="font-size: 3rem;"></i>
      </div>
      
      <h4 class="mb-3">Hasło zostało zmienione!</h4>
      
      <p class="mb-4">Możesz teraz zalogować się używając nowego hasła.</p>
      
      <div class="d-grid gap-2">
        <router-link to="/login" class="btn btn-primary">Przejdź do logowania</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useApi } from '../../composables/useApi';
import { useRoute } from 'vue-router';

// Get the route to extract token from query params
const route = useRoute();

// State
const formData = reactive({
  password: '',
  passwordConfirm: '',
  token: '' // This would be the reset token from the URL
});

const validationErrors = reactive({
  password: '',
  passwordConfirm: '',
  token: '',
  general: ''
});

const isLoading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const passwordChanged = ref(false);
const tokenInvalid = ref(false);
const api = useApi();

// Get token from URL on component mount
onMounted(() => {
  // Get token from route query params
  const token = route.query.token as string;
  
  if (token) {
    formData.token = token;
  } else {
    tokenInvalid.value = true;
    validationErrors.token = 'Link resetujący jest nieprawidłowy lub wygasł.';
  }
});

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
  validationErrors.password = '';
  validationErrors.passwordConfirm = '';
  validationErrors.general = '';

  // Check if token exists
  if (!formData.token) {
    validationErrors.token = 'Link resetujący jest nieprawidłowy lub wygasł.';
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

  return isValid;
}

// Handle password change form submission
async function handlePasswordChange() {
  if (!validate()) return;
  isLoading.value = true;
  try {
    await api.post('/auth/password/reset-confirm', {
      token: formData.token,
      password: formData.password,
      passwordConfirm: formData.passwordConfirm
    });
    passwordChanged.value = true;
  } catch (err: any) {
    if (err.field === 'token') {
      validationErrors.token = err.error;
    } else if (err.field === 'password') {
      validationErrors.password = err.error;
    } else if (err.field === 'passwordConfirm') {
      validationErrors.passwordConfirm = err.error;
    } else {
      validationErrors.general = 'Nie udało się zmienić hasła. Spróbuj ponownie.';
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