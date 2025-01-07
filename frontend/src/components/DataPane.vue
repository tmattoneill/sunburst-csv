<script setup>
import { ref } from 'vue'

const childData = ref([
  'Malware Type 1: 245',
  'Malware Type 2: 189',
  'Malware Type 3: 133',
  'Malware Type 4: 101',
])
</script>

<template>
    <div class="card">
      <h1 class="card-header">Root Value</h1>
    </div>
    <div class="card-body">
      <ul class="list-unstyled">
        <li v-for="(value, index) in childData"
            :key="index"
            class="py-2 text-secondary">
          {{ value }}
        </li>
      </ul>
    </div>
</template>

<style scoped>
/* No custom styles needed - using Bootstrap classes */
</style>