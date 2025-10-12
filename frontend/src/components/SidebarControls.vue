<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  chartName: {
    type: String,
    default: ''
  },
  aggregationMode: {
    type: String,
    default: ''
  },
  valueColumn: {
    type: String,
    default: ''
  },
  treeOrder: {
    type: Array,
    default: () => []
  },
  activeTreeOrder: {
    type: Array,
    default: () => []
  },
  paletteName: {
    type: String,
    default: 'Ocean'
  },
  paletteOptions: {
    type: Array,
    default: () => []
  },
  hasData: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:paletteName', 'update:treeOrder', 'refresh'])

const localOrder = ref([...props.treeOrder])
const draggingIndex = ref(null)

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

watch(() => props.treeOrder, (newOrder) => {
  localOrder.value = [...newOrder]
}, { immediate: true })

const modeLabel = computed(() => {
  const mode = props.aggregationMode?.toUpperCase?.() || ''
  if (mode === 'SUM') return 'Summing values'
  if (mode === 'COUNT_DISTINCT') return 'Counting unique values'
  if (mode === 'COUNT_TOTAL') return 'Counting all rows'
  return props.aggregationMode ? humanize(props.aggregationMode) : 'Unknown mode'
})

const hasPendingChanges = computed(() => {
  if (localOrder.value.length !== props.activeTreeOrder.length) return true
  return localOrder.value.some((field, idx) => field !== props.activeTreeOrder[idx])
})

const handlePaletteChange = (event) => {
  emit('update:paletteName', event.target.value)
}

const onDragStart = (index) => {
  draggingIndex.value = index
}

const onDragOver = (event) => {
  event.preventDefault()
}

const onDrop = (index) => {
  if (draggingIndex.value === null) return
  const updated = [...localOrder.value]
  const [moved] = updated.splice(draggingIndex.value, 1)
  updated.splice(index, 0, moved)
  draggingIndex.value = null
  localOrder.value = updated
  emit('update:treeOrder', updated)
}

const onDragEnd = () => {
  draggingIndex.value = null
}

const refreshDisabled = computed(() => !props.hasData || !hasPendingChanges.value)

const handleRefresh = () => {
  if (refreshDisabled.value) return
  emit('refresh')
}
</script>

<template>
  <aside class="sidebar-control">
    <section class="section">
      <h6 class="section-title">Current Data Set</h6>
      <p class="dataset-name mb-1" :class="{ 'text-muted': !chartName }">
        {{ chartName || 'No dataset loaded' }}
      </p>
      <p v-if="valueColumn" class="detail mb-1">Value Field: <span>{{ humanize(valueColumn) }}</span></p>
      <p v-if="aggregationMode" class="detail mb-0">Mode: <span>{{ modeLabel }}</span></p>
    </section>

    <section class="section">
      <h6 class="section-title">Hierarchy Order</h6>
      <p class="text-muted small mb-2" v-if="!localOrder.length">No hierarchy fields available.</p>
      <div v-else class="field-stack">
        <div
          v-for="(field, index) in localOrder"
          :key="field"
          class="field-card"
          draggable="true"
          @dragstart="() => onDragStart(index)"
          @dragover="onDragOver"
          @drop="() => onDrop(index)"
          @dragend="onDragEnd"
        >
          <span class="handle" aria-hidden="true"><i class="bi bi-grip-vertical"></i></span>
          <span class="field-name">{{ humanize(field) }}</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h6 class="section-title">Palette</h6>
      <select class="form-select form-select-sm" :value="paletteName" @change="handlePaletteChange">
        <option v-for="name in paletteOptions" :key="name" :value="name">{{ name }}</option>
      </select>
    </section>

    <div class="mt-auto pt-3">
      <button
        type="button"
        class="btn btn-primary w-100"
        :disabled="refreshDisabled"
        @click="handleRefresh"
      >
        Refresh Visualization
      </button>
      <p class="text-muted small mt-2 mb-0">
        Drag fields to adjust hierarchy, then refresh to apply changes.
      </p>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-control {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.08);
  min-height: 100%;
}

.section + .section {
  margin-top: 1.5rem;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2933;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.dataset-name {
  font-weight: 600;
  color: #0f172a;
}

.detail {
  font-size: 0.85rem;
  color: #6b7280;
}

.detail span {
  color: #1f2933;
  font-weight: 500;
}

.field-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.field-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 10px;
  background: #f8fafc;
  cursor: grab;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.field-card:active {
  cursor: grabbing;
}

.field-card:hover {
  background: #eef2ff;
  border-color: #4f46e5;
}

.handle {
  color: #94a3b8;
  font-size: 1.1rem;
}

.field-name {
  font-weight: 500;
  color: #1f2933;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 991px) {
  .sidebar-control {
    margin-bottom: 1.5rem;
  }
}
</style>
