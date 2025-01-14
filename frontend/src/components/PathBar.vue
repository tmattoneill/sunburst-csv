<!-- PathBar.vue -->
<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  pathSegments: {
    type: Array,
    required: true,
    default: () => []
  },
  activeIndex: {
    type: Number,
    default: -1
  }
})

const emit = defineEmits(['navigate-to'])

const handleNavigate = (segment, index) => {
  emit('navigate-to', { segment, index })
  console.log(segment, index)
}
</script>

<template>
  <!-- Update the span click handler to pass index -->
  <nav class="path-bar" v-if="pathSegments.length">
    <span
      v-for="(segment, index) in pathSegments"
      :key="index"
      class="path-segment"
      :class="{ active: index === activeIndex }"
      @click="handleNavigate(segment, index)"
    >
      {{ segment.name }}
    </span>
  </nav>
</template>

<style scoped>
.path-bar {
  background: var(--bs-dark);
  padding: 8px;
  border-radius: 6px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.path-segment {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  color: #fff;
  text-decoration: none;
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  cursor: pointer;
  font-weight: normal;
  white-space: nowrap;
}

.path-segment.active {
  background: #4b72c4;
  font-weight: bold;
  color: #fff;
}

.path-segment:not(.active):hover {
  background: rgba(255, 255, 255, 0.2);
}

.path-segment::after {
  content: "";
  margin-left: 8px;
  opacity: 0.5;
}

.path-segment:last-child::after {
  display: none;
}
</style>