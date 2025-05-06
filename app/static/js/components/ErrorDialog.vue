<template>
  <v-dialog
    v-model="show"
    persistent
    max-width="400"
    role="alertdialog"
    aria-modal="true"
    aria-labelledby="error-dialog-title"
  >
    <v-card>
      <v-card-title id="error-dialog-title" class="text-h5 text-center pa-4">
        <v-icon color="error" size="large" class="mr-2">mdi-alert-circle</v-icon>
        Błąd
      </v-card-title>

      <v-card-text class="text-center pa-4">
        {{ message }}
      </v-card-text>

      <v-card-actions class="justify-center pa-4">
        <v-btn
          color="primary"
          variant="elevated"
          @click="$emit('retry')"
          aria-label="Spróbuj ponownie"
        >
          Spróbuj ponownie
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  message: string | null;
}>();

const emit = defineEmits<{
  retry: [];
}>();

// Dialog is only shown when there's an error message
const show = computed(() => !!props.message);
</script>

<style scoped>
/* No additional styling needed - using Vuetify's built-in styles */
</style> 