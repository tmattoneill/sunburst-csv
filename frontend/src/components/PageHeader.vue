<!-- PageHeader.vue -->
<script setup>
import { computed } from 'vue'
import PathBar from './PathBar.vue'

// Props
const props = defineProps({
  reportType: {
    type: String,
    default: ''
  },
  chartName: {
    type: String,
    required: true
  },
  dateStart: {
    type: String,
    default: ''
  },
  dateEnd: {
    type: String,
    default: ''
  },
  treeOrder: {
    type: Array,
    default: () => []
  },
  currentPath: {
    type: Array,
    default: () => []
  }
})

// Check if dates are available (legacy mode)
const hasDates = computed(() => props.dateStart && props.dateEnd)

const emit = defineEmits(['navigate-to'])

// Format path segments
const formattedPathSegments = computed(() => {
  return props.currentPath.map(segment => ({
    name: segment.name,
    id: segment.id,
    value: segment.value,
    nodeId: segment.nodeId // If this exists in your data
  }))
})

// And add a handler for the PathBar navigation:
const handlePathNavigation = (event) => {
  emit('navigate-to', event)
}

</script>

<template>
  <div class="row mb-4">
    <div class="col-12 position-relative">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3>{{ chartName }}</h3>
          <p v-if="reportType" class="text-muted mb-0 small">Type: {{ reportType }}</p>
          <p v-if="treeOrder.length > 0" class="text-muted mb-0 small">
            Hierarchy: {{ treeOrder.join(' → ') }}
          </p>
        </div>
      </div>

      <!-- PathBar -->
      <PathBar
          :pathSegments="formattedPathSegments"
          :activeIndex="formattedPathSegments.length - 1"
          @navigate-to="handlePathNavigation"
      />

      <!-- Dates (optional - shown only for legacy reports) -->
      <div v-if="hasDates" class="mt-3 ps-2">
        <h5 class="mb-1">From: {{ dateStart }}</h5>
        <h5 class="mb-0">To: {{ dateEnd }}</h5>
      </div>
    </div>
  </div>
</template>

