<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '../markdown'

const props = defineProps({
  source: { type: String, default: '' }
})

const html = computed(() => renderMarkdown(props.source))
</script>

<template>
  <div class="md" v-html="html"></div>
</template>
