<template>
  <div class="settings-page">
    <AccountSettings />
  </div>
</template>

<script setup lang="ts">
import AccountSettings from '../components/auth/AccountSettings.vue';
</script>

<style scoped>
.settings-page {
  padding: 2rem;
  background-color: #f5f5f5;
  min-height: 100vh;
}
</style> 