<template>
  <ConfirmDialog
    ref="confirmRef"
    :title="title"
    :message="message"
    confirm-button-text="Usuń"
    :persistent="true"
    @confirm="$emit('confirm')"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ConfirmDialog from './ConfirmDialog.vue';

const props = defineProps({
  title: {
    type: String,
    default: 'Usunąć kategorię?',
  },
  message: {
    type: String,
    default: 'Czy na pewno chcesz usunąć tę kategorię? Tej operacji nie można cofnąć.',
  },
});

const confirmRef = ref<InstanceType<typeof ConfirmDialog> | null>(null);

function open() {
  confirmRef.value?.open();
}

defineExpose({ open });
</script> 