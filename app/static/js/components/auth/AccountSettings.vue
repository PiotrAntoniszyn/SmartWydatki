<template>
  <div class="account-settings">
    <h2 class="mb-4">Ustawienia konta</h2>
    
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">Zmiana hasła</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleChangePassword">
          <!-- Current Password field -->
          <div class="mb-3">
            <label for="current-password" class="form-label required">Obecne hasło</label>
            <div class="input-group">
              <input
                :type="showCurrentPassword ? 'text' : 'password'"
                class="form-control"
                id="current-password"
                v-model="passwordFormData.currentPassword"
                required
                placeholder="Twoje obecne hasło"
                :class="{ 'is-invalid': passwordValidationErrors.currentPassword }"
              />
              <button 
                class="btn btn-outline-secondary" 
                type="button"
                @click="toggleCurrentPasswordVisibility"
              >
                <i class="bi" :class="showCurrentPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
              </button>
              <div class="invalid-feedback" v-if="passwordValidationErrors.currentPassword">
                {{ passwordValidationErrors.currentPassword }}
              </div>
            </div>
          </div>

          <!-- New Password field -->
          <div class="mb-3">
            <label for="new-password" class="form-label required">Nowe hasło</label>
            <div class="input-group">
              <input
                :type="showNewPassword ? 'text' : 'password'"
                class="form-control"
                id="new-password"
                v-model="passwordFormData.newPassword"
                required
                placeholder="Minimum 8 znaków"
                :class="{ 'is-invalid': passwordValidationErrors.newPassword }"
              />
              <button 
                class="btn btn-outline-secondary" 
                type="button"
                @click="toggleNewPasswordVisibility"
              >
                <i class="bi" :class="showNewPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
              </button>
              <div class="invalid-feedback" v-if="passwordValidationErrors.newPassword">
                {{ passwordValidationErrors.newPassword }}
              </div>
            </div>
            <div class="form-text">Hasło musi mieć co najmniej 8 znaków.</div>
          </div>

          <!-- Confirm New Password field -->
          <div class="mb-3">
            <label for="confirm-new-password" class="form-label required">Potwierdź nowe hasło</label>
            <div class="input-group">
              <input
                :type="showConfirmNewPassword ? 'text' : 'password'"
                class="form-control"
                id="confirm-new-password"
                v-model="passwordFormData.confirmNewPassword"
                required
                placeholder="Powtórz nowe hasło"
                :class="{ 'is-invalid': passwordValidationErrors.confirmNewPassword }"
              />
              <button 
                class="btn btn-outline-secondary" 
                type="button"
                @click="toggleConfirmNewPasswordVisibility"
              >
                <i class="bi" :class="showConfirmNewPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
              </button>
              <div class="invalid-feedback" v-if="passwordValidationErrors.confirmNewPassword">
                {{ passwordValidationErrors.confirmNewPassword }}
              </div>
            </div>
          </div>

          <!-- Password change alert -->
          <div v-if="passwordChangeSuccess" class="alert alert-success mb-3" role="alert">
            <i class="bi bi-check-circle me-2"></i> Hasło zostało zmienione pomyślnie.
          </div>

          <!-- Submit button -->
          <button 
            type="submit" 
            class="btn btn-primary"
            :disabled="passwordChangeLoading"
          >
            <span v-if="passwordChangeLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Zmień hasło
          </button>
        </form>
      </div>
    </div>

    <div class="card mb-4 border-danger">
      <div class="card-header bg-danger text-white">
        <h5 class="mb-0">Usunięcie konta</h5>
      </div>
      <div class="card-body">
        <p>Usunięcie konta spowoduje trwałe usunięcie wszystkich Twoich danych z systemu, zgodnie z wymogami RODO.</p>
        <p class="mb-4"><strong>Uwaga:</strong> Po usunięciu konta nie będzie możliwości odzyskania Twoich danych.</p>
        
        <button 
          type="button" 
          class="btn btn-danger"
          @click="showDeleteConfirmation = true"
        >
          <i class="bi bi-trash me-2"></i> Usuń konto
        </button>
      </div>
    </div>

    <!-- Delete Account Confirmation Modal -->
    <div
      class="modal fade"
      ref="deleteModal"
      tabindex="-1"
      aria-hidden="true"
      data-bs-backdrop="static"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">
              <i class="bi bi-exclamation-triangle me-2"></i>
              Potwierdź usunięcie konta
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Zamknij"></button>
          </div>
          <div class="modal-body">
            <p>Czy na pewno chcesz usunąć swoje konto? Tej operacji <strong>nie można</strong> cofnąć.</p>
            
            <p>Wszystkie Twoje dane zostaną trwale usunięte z naszego systemu.</p>

            <!-- Confirm with password -->
            <div class="mb-3">
              <label for="delete-confirm-password" class="form-label required">Potwierdź hasłem</label>
              <div class="input-group">
                <input
                  :type="showDeleteConfirmPassword ? 'text' : 'password'"
                  class="form-control"
                  id="delete-confirm-password"
                  v-model="deleteConfirmPassword"
                  required
                  placeholder="Wprowadź swoje hasło"
                  :class="{ 'is-invalid': deletePasswordError }"
                />
                <button 
                  class="btn btn-outline-secondary" 
                  type="button"
                  @click="toggleDeleteConfirmPasswordVisibility"
                >
                  <i class="bi" :class="showDeleteConfirmPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
                <div class="invalid-feedback" v-if="deletePasswordError">
                  {{ deletePasswordError }}
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Anuluj</button>
            <button 
              type="button" 
              class="btn btn-danger"
              @click="handleDeleteAccount"
              :disabled="deleteAccountLoading"
            >
              <span v-if="deleteAccountLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Usuń konto
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watchEffect } from 'vue';
import { useApi } from '../../composables/useApi';
import { useAuth } from '../../composables/useAuth';
// Import type only to avoid linter errors
import type { Modal as BootstrapModal } from 'bootstrap';

// State for password change
const passwordFormData = reactive({
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: ''
});

const passwordValidationErrors = reactive({
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: '',
  general: ''
});

const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmNewPassword = ref(false);
const passwordChangeLoading = ref(false);
const passwordChangeSuccess = ref(false);
const api = useApi();

// State for account deletion
const deleteModal = ref<HTMLElement | null>(null);
const showDeleteConfirmation = ref(false);
const deleteConfirmPassword = ref('');
const showDeleteConfirmPassword = ref(false);
const deletePasswordError = ref('');
const deleteAccountLoading = ref(false);
const auth = useAuth();
let modal: BootstrapModal | null = null;

// Setup Bootstrap modal on component mount
onMounted(() => {
  if (deleteModal.value) {
    // Explicit cast to any to satisfy TS until global types are available
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    if (w.bootstrap) {
      modal = new w.bootstrap.Modal(deleteModal.value);
    }
  }

  // Watch showDeleteConfirmation to open/close modal
  watchEffect(() => {
    if (showDeleteConfirmation.value) {
      modal?.show();
    } else {
      modal?.hide();
    }
  });

  // Listen for modal hidden event to reset state
  if (deleteModal.value) {
    deleteModal.value.addEventListener('hidden.bs.modal', () => {
      showDeleteConfirmation.value = false;
      deleteConfirmPassword.value = '';
      deletePasswordError.value = '';
    });
  }
});

// Toggle password visibility functions
function toggleCurrentPasswordVisibility() {
  showCurrentPassword.value = !showCurrentPassword.value;
}

function toggleNewPasswordVisibility() {
  showNewPassword.value = !showNewPassword.value;
}

function toggleConfirmNewPasswordVisibility() {
  showConfirmNewPassword.value = !showConfirmNewPassword.value;
}

function toggleDeleteConfirmPasswordVisibility() {
  showDeleteConfirmPassword.value = !showDeleteConfirmPassword.value;
}

// Password change validation
function validatePasswordChange(): boolean {
  let isValid = true;
  
  // Reset errors
  passwordValidationErrors.currentPassword = '';
  passwordValidationErrors.newPassword = '';
  passwordValidationErrors.confirmNewPassword = '';
  passwordValidationErrors.general = '';

  // Current password validation
  if (!passwordFormData.currentPassword) {
    passwordValidationErrors.currentPassword = 'Obecne hasło jest wymagane';
    isValid = false;
  }

  // New password validation
  if (!passwordFormData.newPassword) {
    passwordValidationErrors.newPassword = 'Nowe hasło jest wymagane';
    isValid = false;
  } else if (passwordFormData.newPassword.length < 8) {
    passwordValidationErrors.newPassword = 'Hasło musi mieć co najmniej 8 znaków';
    isValid = false;
  }

  // Confirm new password validation
  if (!passwordFormData.confirmNewPassword) {
    passwordValidationErrors.confirmNewPassword = 'Potwierdzenie hasła jest wymagane';
    isValid = false;
  } else if (passwordFormData.newPassword !== passwordFormData.confirmNewPassword) {
    passwordValidationErrors.confirmNewPassword = 'Hasła nie są identyczne';
    isValid = false;
  }

  return isValid;
}

// Handle password change form submission
async function handleChangePassword() {
  passwordChangeSuccess.value = false;
  if (!validatePasswordChange()) return;
  passwordChangeLoading.value = true;
  try {
    await api.post('/auth/password/change', {
      currentPassword: passwordFormData.currentPassword,
      newPassword: passwordFormData.newPassword,
      passwordConfirm: passwordFormData.confirmNewPassword
    });
    passwordChangeSuccess.value = true;
    // Reset form
    passwordFormData.currentPassword = '';
    passwordFormData.newPassword = '';
    passwordFormData.confirmNewPassword = '';
  } catch (err: any) {
    // Field errors
    if (err.field && err.error) {
      passwordValidationErrors[err.field] = err.error;
    } else {
      passwordValidationErrors.general = typeof err === 'string' ? err : 'Nie udało się zmienić hasła. Spróbuj ponownie.';
    }
  } finally {
    passwordChangeLoading.value = false;
  }
}

// Handle account deletion
async function handleDeleteAccount() {
  // Validate password
  if (!deleteConfirmPassword.value) {
    deletePasswordError.value = 'Hasło jest wymagane';
    return;
  }
  deleteAccountLoading.value = true;
  try {
    await api.delete('/auth/account');
    // Logout and redirect
    auth.logout();
  } catch (err: any) {
    if (err.field === 'password') {
      deletePasswordError.value = err.error;
    } else {
      deletePasswordError.value = 'Nie udało się usunąć konta. Spróbuj ponownie.';
    }
  } finally {
    deleteAccountLoading.value = false;
  }
}
</script>

<style scoped>
.required::after {
  content: '*';
  color: #dc3545;
  margin-left: 2px;
}
</style> 