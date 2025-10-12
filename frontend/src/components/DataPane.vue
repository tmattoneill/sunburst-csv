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
  },
  valueColumn: {
    type: String,
    required: false,
    default: ''
  },
  aggregationMode: {
    type: String,
    required: false,
    default: ''
  },
  treeOrder: {
    type: Array,
    required: false,
    default: () => []
  }
})


// Add number formatting helper
const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const humanize = (text = '') => {
  return text
    .replace(/[_\-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const pluralize = (label) => {
  if (!label) return ''
  const lower = label.toLowerCase()
  if (lower.endsWith('data')) return label
  if (lower.endsWith('ies')) return label
  if (lower.endsWith('s')) return label
  if (lower.endsWith('y')) {
    return label.slice(0, -1) + 'ies'
  }
  return `${label}s`
}

const resolvedFieldName = computed(() => {
  if (props.valueColumn) {
    return humanize(props.valueColumn)
  }

  if (props.aggregationMode && props.treeOrder?.length) {
    return humanize(props.treeOrder[props.treeOrder.length - 1])
  }

  return ''
})

// Format value label based on aggregation mode
const valueLabel = computed(() => {
  const mode = props.aggregationMode?.toUpperCase?.() || ''
  const base = resolvedFieldName.value

  if (!mode && !base) {
    return 'Tags with Incidents' // Legacy default
  }

  if (mode === 'SUM') {
    return base ? `Total ${base}` : 'Total Value'
  }

  if (mode === 'COUNT_DISTINCT') {
    const label = base ? pluralize(base) : 'Records'
    return `Unique ${label}`
  }

  if (mode === 'COUNT_TOTAL') {
    const label = base ? pluralize(base) : 'Records'
    return `Total ${label}`
  }

  return base || 'Total Value'
})

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
      <p class="mb-0 text-secondary">{{ valueLabel }}: {{ formatNumber(rootValue) }}</p>
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
