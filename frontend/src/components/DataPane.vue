<!-- DataPane.vue -->
<script setup>
import { computed } from 'vue'

const props = defineProps({
  rootName: {
    type: String,
    required: true,
    default: ''
  },
  rootValue: {
    type: Number,
    required: true,
    default: 0
  },
  topChildren: {
    type: Array,
    required: true,
    default: () => []
  }
})


// Add number formatting helper
const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const displayChildren = computed(() => {
  if (!props.topChildren?.length) return []

  const sortedChildren = [...props.topChildren]
      .sort((a, b) => b.value - a.value)

  if (sortedChildren.length <= 10) {
    return sortedChildren
  }

  const top10 = sortedChildren.slice(0, 10)
  const otherSum = sortedChildren
      .slice(10)
      .reduce((sum, child) => sum + (child.value || 0), 0)

  return [
    ...top10,
    { name: 'Other', value: otherSum }
  ]
})
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h5 class="mb-0">{{ rootName || 'No Data' }}</h5>
      <p class="mb-0 text-secondary">Tags with Incidents: {{ formatNumber(rootValue) }}</p>
    </div>
    <div class="card-body">
      <ul class="list-unstyled mb-0">
        <li v-for="child in displayChildren"
            :key="child.name"
            class="py-2 border-bottom">
          <div class="d-flex justify-content-between">
            <span>{{ child.name }}</span>
            <span class="text-secondary">{{ formatNumber(child.value) }}</span>
          </div>
        </li>
      </ul>
      <p v-if="!displayChildren.length" class="text-center text-secondary mb-0 py-3">
        No data available
      </p>
    </div>
  </div>
</template>