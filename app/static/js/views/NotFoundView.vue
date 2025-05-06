<template>
  <div class="not-found-container">
    <v-card class="not-found-card mx-auto" max-width="500">
      <v-card-title class="text-h3 text-center">
        404
      </v-card-title>
      
      <v-card-subtitle class="text-h5 text-center mb-4">
        Strona nie znaleziona
      </v-card-subtitle>
      
      <v-card-text class="text-center">
        <p class="mb-5">
          Przepraszamy, ale strona której szukasz nie istnieje lub została przeniesiona.
        </p>
        
        <v-btn
          color="primary"
          @click="goHome"
          class="mt-4"
        >
          Wróć do strony głównej
        </v-btn>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background-color: #f5f5f5;
}

.not-found-card {
  padding: 2rem;
}
</style> 