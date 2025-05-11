<template>
  <div class="login-container">
    <v-card class="login-card mx-auto" max-width="500">
      <v-card-title class="text-h4 text-center pa-4">
        Logowanie
      </v-card-title>
      
      <v-card-text>
        <v-form @submit.prevent="handleLogin" ref="form">
          <v-text-field
            v-model="email"
            label="Email"
            type="email"
            required
            :rules="[v => !!v || 'Email jest wymagany', v => /.+@.+\..+/.test(v) || 'Email musi być poprawny']"
            autocomplete="email"
            aria-label="Email"
          ></v-text-field>
          
          <v-text-field
            v-model="password"
            label="Hasło"
            type="password"
            required
            :rules="[v => !!v || 'Hasło jest wymagane']"
            autocomplete="current-password"
            aria-label="Hasło"
          ></v-text-field>
          
          <v-alert
            v-if="auth.error"
            type="error"
            class="mb-4"
            role="alert"
          >
            {{ auth.error }}
          </v-alert>
          
          <div class="d-flex flex-column">
            <v-btn
              type="submit"
              color="primary"
              block
              class="mt-4"
              :loading="auth.loading"
              :disabled="auth.loading"
            >
              Zaloguj się
            </v-btn>
            
            <v-btn
              variant="text"
              class="mt-2"
              @click="$router.push('/register')"
            >
              Nie masz konta? Zarejestruj się
            </v-btn>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const router = useRouter();
const auth = useAuth();
const form = ref<any>(null);
const email = ref('');
const password = ref('');

// Login handler using auth composable
const handleLogin = async () => {
  // Validate form
  const isValid = form.value && await form.value.validate();
  
  if (!isValid.valid) {
    return;
  }
  
  // Use auth composable for login
  const success = await auth.login(email.value, password.value);
  
  if (success) {
    // After login, navigate to dashboard
    router.push('/dashboard');
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background-color: #f5f5f5;
}

.login-card {
  width: 100%;
  padding: 1rem;
}
</style> 