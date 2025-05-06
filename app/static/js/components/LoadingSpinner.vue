<template>
  <div
    class="loading-spinner"
    role="status"
    aria-live="polite"
    aria-label="Ładowanie danych"
  >
    <v-progress-circular
      indeterminate
      color="primary"
      size="64"
      width="6"
    />
    <span class="loading-text">Ładowanie...</span>
  </div>
</template>

<script setup lang="ts">
// Standard Vuetify spinner, no additional props or logic needed
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 2rem 0;
  gap: 1rem;
}

.loading-text {
  margin-top: 1rem;
  font-size: 1rem;
  color: rgba(0, 0, 0, 0.6);
}
</style> 