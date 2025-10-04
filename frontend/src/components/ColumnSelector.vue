<!-- ColumnSelector.vue: Drag-and-drop column selector for building hierarchy -->
<template>
  <div class="column-selector">
    <div class="row">
      <!-- Left Panel: Available Columns -->
      <div class="col-md-6">
        <div class="panel available-columns">
          <h6 class="panel-title">Available Columns</h6>
          <p class="text-muted small">Click to add to hierarchy →</p>

          <div class="column-list">
            <div
              v-for="col in availableColumns"
              :key="col.name"
              class="column-item"
              :class="{ 'disabled': isColumnSelected(col.name) }"
              @click="addColumn(col.name)"
            >
              <div class="column-info">
                <span class="column-icon">
                  {{ col.type === 'numeric' ? '📊' : '📝' }}
                </span>
                <span class="column-name">{{ col.name }}</span>
              </div>
              <div class="column-sample">
                <small class="text-muted">{{ formatSample(col.sample) }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Selected Hierarchy -->
      <div class="col-md-6">
        <div class="panel selected-columns">
          <h6 class="panel-title">Hierarchy Order</h6>
          <p class="text-muted small">Drag to reorder, min 3 required</p>

          <div
            v-if="selectedOrder.length === 0"
            class="empty-state"
          >
            <i class="bi bi-arrow-left"></i>
            <p>Select columns from the left to build your hierarchy</p>
          </div>

          <div
            v-else
            class="selected-list"
          >
            <div
              v-for="(colName, index) in selectedOrder"
              :key="colName"
              class="selected-item"
              draggable="true"
              @dragstart="handleDragStart(index)"
              @dragover.prevent
              @drop="handleDrop(index)"
            >
              <div class="item-header">
                <span class="item-number">{{ index + 1 }}</span>
                <span class="item-name">{{ colName }}</span>
                <button
                  class="btn btn-sm btn-link text-danger"
                  @click="removeColumn(index)"
                  title="Remove"
                >
                  <i class="bi bi-x-lg"></i>
                </button>
              </div>
              <div class="item-controls">
                <button
                  class="btn btn-sm btn-outline-secondary"
                  @click="moveUp(index)"
                  :disabled="index === 0"
                  title="Move up"
                >
                  <i class="bi bi-arrow-up"></i>
                </button>
                <button
                  class="btn btn-sm btn-outline-secondary"
                  @click="moveDown(index)"
                  :disabled="index === selectedOrder.length - 1"
                  title="Move down"
                >
                  <i class="bi bi-arrow-down"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Validation Feedback -->
          <div class="validation-feedback mt-3">
            <div
              v-if="selectedOrder.length < 3"
              class="alert alert-warning small"
            >
              ⚠️ Select at least {{ 3 - selectedOrder.length }} more column(s)
            </div>
            <div
              v-else
              class="alert alert-success small"
            >
              ✅ {{ selectedOrder.length }} columns selected - good to go!
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: false,
    default: () => []
  },
  modelValue: {
    type: Array,
    default: () => []
  }
})

// Debug logging
console.log('ColumnSelector - Received props.columns:', props.columns)
console.log('ColumnSelector - Columns length:', props.columns?.length)

const emit = defineEmits(['update:modelValue'])

const selectedOrder = ref([...props.modelValue])
const draggedIndex = ref(null)

// Filter out columns already selected
const availableColumns = computed(() => {
  console.log('ColumnSelector - Computing availableColumns, props.columns:', props.columns)
  console.log('ColumnSelector - selectedOrder:', selectedOrder.value)
  const filtered = props.columns.filter(col => !selectedOrder.value.includes(col.name))
  console.log('ColumnSelector - availableColumns result:', filtered)
  return filtered
})

const isColumnSelected = (colName) => {
  return selectedOrder.value.includes(colName)
}

const addColumn = (colName) => {
  if (!isColumnSelected(colName)) {
    selectedOrder.value.push(colName)
    emit('update:modelValue', selectedOrder.value)
  }
}

const removeColumn = (index) => {
  selectedOrder.value.splice(index, 1)
  emit('update:modelValue', selectedOrder.value)
}

const moveUp = (index) => {
  if (index > 0) {
    const item = selectedOrder.value[index]
    selectedOrder.value.splice(index, 1)
    selectedOrder.value.splice(index - 1, 0, item)
    emit('update:modelValue', selectedOrder.value)
  }
}

const moveDown = (index) => {
  if (index < selectedOrder.value.length - 1) {
    const item = selectedOrder.value[index]
    selectedOrder.value.splice(index, 1)
    selectedOrder.value.splice(index + 1, 0, item)
    emit('update:modelValue', selectedOrder.value)
  }
}

const handleDragStart = (index) => {
  draggedIndex.value = index
}

const handleDrop = (dropIndex) => {
  if (draggedIndex.value !== null && draggedIndex.value !== dropIndex) {
    const item = selectedOrder.value[draggedIndex.value]
    selectedOrder.value.splice(draggedIndex.value, 1)
    selectedOrder.value.splice(dropIndex, 0, item)
    emit('update:modelValue', selectedOrder.value)
  }
  draggedIndex.value = null
}

const formatSample = (sample) => {
  if (sample === null || sample === undefined) return 'N/A'
  const sampleStr = String(sample)
  return sampleStr.length > 30 ? sampleStr.substring(0, 30) + '...' : sampleStr
}

// Watch for changes to columns prop
watch(() => props.columns, (newVal, oldVal) => {
  console.log('ColumnSelector - props.columns changed!')
  console.log('  Old:', oldVal)
  console.log('  New:', newVal)
}, { deep: true, immediate: true })

// Watch for external changes to modelValue
watch(() => props.modelValue, (newVal) => {
  selectedOrder.value = [...newVal]
}, { deep: true })
</script>

<style scoped>
.column-selector {
  width: 100%;
}

.panel {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  min-height: 400px;
}

.panel-title {
  margin: 0 0 0.5rem 0;
  font-weight: 600;
  color: #212529;
}

.column-list {
  max-height: 350px;
  overflow-y: auto;
  margin-top: 0.5rem;
}

.column-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.column-item:hover:not(.disabled) {
  border-color: #0d6efd;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transform: translateX(4px);
}

.column-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.column-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.column-icon {
  font-size: 1.2rem;
}

.column-name {
  font-weight: 500;
  color: #212529;
}

.column-sample {
  padding-left: 2rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 250px;
  color: #6c757d;
  text-align: center;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.selected-list {
  max-height: 300px;
  overflow-y: auto;
}

.selected-item {
  background: white;
  border: 2px solid #0d6efd;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  cursor: move;
  transition: all 0.2s;
}

.selected-item:hover {
  box-shadow: 0 2px 6px rgba(13, 110, 253, 0.2);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.item-number {
  background: #0d6efd;
  color: white;
  font-weight: bold;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}

.item-name {
  flex: 1;
  font-weight: 500;
}

.item-controls {
  display: flex;
  gap: 0.25rem;
  justify-content: flex-start;
}

.item-controls .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.85rem;
}

.validation-feedback .alert {
  margin-bottom: 0;
  padding: 0.5rem;
}

/* Scrollbar styling */
.column-list::-webkit-scrollbar,
.selected-list::-webkit-scrollbar {
  width: 6px;
}

.column-list::-webkit-scrollbar-track,
.selected-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.column-list::-webkit-scrollbar-thumb,
.selected-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.column-list::-webkit-scrollbar-thumb:hover,
.selected-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
