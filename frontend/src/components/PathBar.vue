<script setup>
import { ref } from 'vue'

const pathSegments = ref([
  { name: 'Disks and Folders', path: '#' },
  { name: 'Macintosh HDD', path: '#' }
])
const activeIndex = ref(0)
</script>

<template>
  <nav class="path-bar">
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
}

.path-segment {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  color: #fff;
  text-decoration: none;
  position: relative;
}

.path-segment.active {
  background: #4b72c4;
  border-radius: 4px;
}

.path-segment:not(.active) {
  color: rgba(255, 255, 255, 0.8);
}

.path-segment::after {
  content: ">";
  margin-left: 8px;
  opacity: 0.5;
}

.path-segment:last-child::after {
  display: none;
}
</style>