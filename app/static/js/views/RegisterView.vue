<template>
  <div class="register-container">
    <v-card class="register-card mx-auto" max-width="500">
      <v-card-title class="text-h4 text-center pa-4">
        Rejestracja
      </v-card-title>
      
      <v-card-text>
        <v-form @submit.prevent="handleRegister" ref="form">
          <v-text-field
            v-model="name"
            label="Imię i nazwisko"
            type="text"
            required
            :rules="[v => !!v || 'Imię i nazwisko jest wymagane']"
            aria-label="Imię i nazwisko"
          ></v-text-field>
          
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
            :rules="[
              v => !!v || 'Hasło jest wymagane',
              v => v.length >= 8 || 'Hasło musi mieć co najmniej 8 znaków'
            ]"
            autocomplete="new-password"
            aria-label="Hasło"
          ></v-text-field>
          
          <v-text-field
            v-model="confirmPassword"
            label="Potwierdź hasło"
            type="password"
            required
            :rules="[
              v => !!v || 'Potwierdzenie hasła jest wymagane',
              v => v === password || 'Hasła muszą być takie same'
            ]"
            autocomplete="new-password"
            aria-label="Potwierdź hasło"
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
              Zarejestruj się
            </v-btn>
            
            <v-btn
              variant="text"
              class="mt-2"
              @click="$router.push('/login')"
            >
              Masz już konto? Zaloguj się
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
const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

// Register handler using auth composable
const handleRegister = async () => {
  // Validate form
  const isValid = form.value && await form.value.validate();
  
  if (!isValid.valid) {
    return;
  }
  
  // Use auth composable for registration
  const success = await auth.register({
    name: name.value,
    email: email.value, 
    password: password.value
  });
  
  if (success) {
    // After successful registration, redirect to onboarding
    router.push('/onboarding');
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background-color: #f5f5f5;
}

.register-card {
  width: 100%;
  padding: 1rem;
}
</style> 