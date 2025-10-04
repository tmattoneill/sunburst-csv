<!-- PageHeader.vue -->
<script setup>
import { ref, computed } from 'vue'
import { PALETTES } from '@/palettes'
import PathBar from './PathBar.vue'

// Props
const props = defineProps({
  paletteName: {
    type: String,
    default: 'Ocean'
  },
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

const emit = defineEmits(['update:paletteName', 'navigate-to'])

const selectedPalette = ref(props.paletteName)
const colors = ref(PALETTES[props.paletteName] || PALETTES.Ocean)

// Computed palette names for the dropdown
const paletteNames = computed(() => Object.keys(PALETTES))

// Format path segments
// In PageHeader.vue
const formattedPathSegments = computed(() => {
  console.log('Current path in PageHeader:', props.currentPath);
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

// Handle palette changes
const handlePaletteChange = () => {
  colors.value = PALETTES[selectedPalette.value]
  emit('update:paletteName', selectedPalette.value)
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
        <div class="palette-selector">
          <select v-model="selectedPalette" @change="handlePaletteChange" class="form-select form-select-sm w-auto">
            <option v-for="name in paletteNames" :key="name" :value="name">
              {{ name }}
            </option>
          </select>
        </div>
      </div>

      <!-- PathBar -->
      <PathBar
          :pathSegments="formattedPathSegments"
          :activeIndex="formattedPathSegments.length - 1"
          @navigate-to="handlePathNavigation"
      />

      <!-- Dates (optional - shown only for legacy reports) -->
      <div class="mt-3 ps-2 d-flex justify-content-between align-items-end">
        <div v-if="hasDates">
          <h5 class="mb-1">From: {{ dateStart }}</h5>
          <h5 class="mb-0">To: {{ dateEnd }}</h5>
        </div>
        <div v-else>
          <!-- Placeholder to keep layout consistent -->
        </div>
        <button
          class="btn btn-primary px-4"
          id="mdl-btn-load"
          type="button"
          data-bs-toggle="modal"
          data-bs-target="#mdl-load"
        >
          <i class="bi bi-upload me-2"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.palette-selector {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}

.form-select {
  font-size: 0.875rem;
}
</style>