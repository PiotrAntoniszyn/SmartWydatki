<template>
  <div class="new-password-page">
    <NewPasswordForm />
  </div>
</template>

<script setup lang="ts">
import NewPasswordForm from '../components/auth/NewPasswordForm.vue';
</script>

<style scoped>
.new-password-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style> 