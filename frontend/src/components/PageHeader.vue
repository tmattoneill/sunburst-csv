<!-- PageHeader.vue -->
<script setup>
import { defineEmits, defineProps, ref, computed } from 'vue'
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
    required: true
  },
  chartName: {
    type: String,
    required: true
  },
  dateStart: {
    type: String,
    required: true
  },
  dateEnd: {
    type: String,
    required: true
  },
  currentPath: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:paletteName'])

const selectedPalette = ref(props.paletteName)
const colors = ref(PALETTES[props.paletteName] || PALETTES.Ocean)

// Computed palette names for the dropdown
const paletteNames = computed(() => Object.keys(PALETTES))

// Format path segments to include values
const formattedPathSegments = computed(() => {
  return props.currentPath.map(segment => ({
    name: `${segment.name} (${segment.value.toLocaleString()})`,
    path: '#'
  }))
})

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
        <h3>{{ reportType }}: {{ chartName }}</h3>
        <div class="palette-selector">
          <select v-model="selectedPalette" @change="handlePaletteChange" class="form-select form-select-sm w-auto">
            <option v-for="name in paletteNames" :key="name" :value="name">
              {{ name }}
            </option>
          </select>
        </div>
      </div>

      <!-- PathBar -->
      <PathBar :pathSegments="formattedPathSegments" :activeIndex="formattedPathSegments.length - 1" />

      <!-- Dates -->
      <div class="mt-3 ps-2 d-flex justify-content-between align-items-end">
        <div>
          <h5 class="mb-1">From: {{ dateStart }}</h5>
          <h5 class="mb-0">To: {{ dateEnd }}</h5>
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