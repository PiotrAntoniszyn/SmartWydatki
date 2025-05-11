<template>
  <div class="reset-password-page">
    <PasswordResetForm />
  </div>
</template>

<script setup lang="ts">
import PasswordResetForm from '../components/auth/PasswordResetForm.vue';
</script>

<style scoped>
.reset-password-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style> 