<!-- PathBar.vue -->
<script setup>
import { defineProps } from 'vue'

// Props
defineProps({
  pathSegments: {
    type: Array,
    required: true,
    default: () => []
  },
  activeIndex: {
    type: Number,
    default: -1 // No active segment highlighted by default
  }
})

// Navigation placeholder interaction (optional)
const handleNavigate = (segment) => {
  console.log(`Navigating to: ${segment.name}`)
}
</script>

<template>
  <nav class="path-bar" v-if="pathSegments.length">
    <span
      v-for="(segment, index) in pathSegments"
      :key="index"
      class="path-segment"
      :class="{ active: index === activeIndex }"
      @click="handleNavigate(segment)"
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