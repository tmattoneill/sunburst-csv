<!-- FileLoaderModal.vue: Multi-Step Upload Wizard -->
<template>
  <div
    class="modal fade"
    id="mdl-load"
    tabindex="-1"
    aria-labelledby="mdl-load-label"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
          <h5 class="modal-title" id="mdl-load-label">
            {{ stepTitles[currentStep] }}
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            @click="handleClose"
          ></button>
        </div>

        <!-- Progress Indicator -->
        <div class="modal-body">
          <div class="progress-stepper mb-4">
            <div
              v-for="(title, index) in stepTitles"
              :key="index"
              class="step"
              :class="{
                'active': index === currentStep,
                'completed': index < currentStep
              }"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-title">{{ title }}</div>
            </div>
          </div>

          <!-- Step 1: Upload File -->
          <div v-if="currentStep === 0" class="step-content">
            <div class="upload-area text-center">
              <i class="bi bi-cloud-upload display-1 text-primary mb-3"></i>
              <h6>Select a CSV or Excel file</h6>
              <p class="text-muted">Supported formats: CSV, XLS, XLSX</p>
              <input
                type="file"
                @change="handleFileChange"
                accept=".csv,.xls,.xlsx"
                class="form-control w-50 mx-auto"
                ref="fileInput"
              />
              <div v-if="selectedFile" class="mt-3">
                <p class="mb-1"><strong>Selected:</strong> {{ selectedFile.name }}</p>
                <p class="text-muted small">Size: {{ formatFileSize(selectedFile.size) }}</p>
              </div>
            </div>
          </div>

          <!-- Step 2: Configure Hierarchy -->
          <div v-if="currentStep === 1" class="step-content">
            <div v-if="isLoadingFileInfo" class="text-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Analyzing file...</p>
            </div>
            <div v-else>
              <div class="alert alert-info mb-3">
                <i class="bi bi-info-circle"></i>
                Select at least 3 columns to build your hierarchy. Drag to reorder.
              </div>
              <ColumnSelector
                v-model="hierarchyColumns"
                :columns="availableColumns"
              />
            </div>
          </div>

          <!-- Step 3: Select Value Column -->
          <div v-if="currentStep === 2" class="step-content">
            <div class="alert alert-info mb-3">
              <i class="bi bi-info-circle"></i>
              Choose the numeric column whose values will be aggregated in the visualization.
            </div>
            <div class="value-column-selector">
              <h6 class="mb-3">Value Column</h6>
              <div class="row">
                <div
                  v-for="col in numericColumns"
                  :key="col.name"
                  class="col-md-4 mb-3"
                >
                  <div
                    class="value-option"
                    :class="{ 'selected': valueColumn === col.name }"
                    @click="selectValueColumn(col.name)"
                  >
                    <div class="option-header">
                      <span class="option-icon">📊</span>
                      <span class="option-name">{{ col.name }}</span>
                      <i v-if="valueColumn === col.name" class="bi bi-check-circle-fill text-success"></i>
                    </div>
                    <div class="option-sample">
                      <small class="text-muted">Sample: {{ col.sample }}</small>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="numericColumns.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-exclamation-triangle display-4"></i>
                <p class="mt-2">No numeric columns found in your file.</p>
              </div>
            </div>
          </div>

          <!-- Step 4: Name Chart & Process -->
          <div v-if="currentStep === 3" class="step-content">
            <div class="chart-naming">
              <h6 class="mb-3">Name Your Visualization</h6>
              <input
                type="text"
                class="form-control mb-4"
                placeholder="e.g., RTB Ad Spend by DSP and Brand"
                v-model="chartName"
                @keyup.enter="processFile"
                :disabled="isProcessing"
              />

              <!-- Progress Bar (shown when processing) -->
              <div v-if="isProcessing" class="progress-section mb-4">
                <div class="progress" style="height: 30px;">
                  <div
                    class="progress-bar progress-bar-striped progress-bar-animated"
                    role="progressbar"
                    :style="{ width: (progressCurrent / progressTotal * 100) + '%' }"
                    :aria-valuenow="progressCurrent"
                    :aria-valuemin="0"
                    :aria-valuemax="progressTotal"
                  >
                    {{ Math.round(progressCurrent / progressTotal * 100) }}%
                  </div>
                </div>
                <p class="text-center text-muted mt-2 small">
                  {{ progressMessage }}
                </p>
              </div>

              <!-- Summary -->
              <div class="config-summary p-3 bg-light rounded">
                <h6 class="mb-3">Configuration Summary</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p class="mb-2"><strong>File:</strong></p>
                    <p class="text-muted small">{{ uploadedFileName }}</p>
                    <p class="mb-2 mt-3"><strong>Data Rows:</strong></p>
                    <p class="text-muted">{{ fileInfo?.rowCount || 0 }}</p>
                  </div>
                  <div class="col-md-6">
                    <p class="mb-2"><strong>Hierarchy:</strong></p>
                    <ol class="text-muted small ps-3">
                      <li v-for="col in hierarchyColumns" :key="col">{{ col }}</li>
                    </ol>
                    <p class="mb-2 mt-3"><strong>Value Column:</strong></p>
                    <p class="text-muted">{{ valueColumn }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Error/Status Messages -->
          <div v-if="statusMessage" class="mt-3">
            <div
              class="alert"
              :class="statusType === 'success' ? 'alert-success' : statusType === 'error' ? 'alert-danger' : 'alert-info'"
            >
              {{ statusMessage }}
            </div>
          </div>
        </div>

        <!-- Modal Footer with Navigation -->
        <div class="modal-footer">
          <button
            v-if="currentStep > 0"
            type="button"
            class="btn btn-secondary"
            @click="previousStep"
            :disabled="isProcessing"
          >
            <i class="bi bi-arrow-left"></i> Back
          </button>
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
            @click="handleClose"
            :disabled="isProcessing"
          >
            Cancel
          </button>
          <button
            v-if="currentStep < 3"
            type="button"
            class="btn btn-primary"
            @click="nextStep"
            :disabled="!canProceed || isProcessing"
          >
            Next <i class="bi bi-arrow-right"></i>
          </button>
          <button
            v-if="currentStep === 3"
            type="button"
            class="btn btn-success"
            @click="processFile"
            :disabled="!canProcess || isProcessing"
          >
            <span v-if="isProcessing">
              <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Processing...
            </span>
            <span v-else>
              <i class="bi bi-check-lg"></i> Create Visualization
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchApi, API_ENDPOINTS } from '@/services/api'
import ColumnSelector from './ColumnSelector.vue'

// Props
const props = defineProps({
  sessionId: {
    type: String,
    required: true
  }
})

// Component state
const currentStep = ref(0)
const selectedFile = ref(null)
const uploadedFileName = ref('')
const fileInfo = ref(null)
const isLoadingFileInfo = ref(false)
const hierarchyColumns = ref([])
const valueColumn = ref('')
const chartName = ref('')
const statusMessage = ref('')
const statusType = ref('')
const isProcessing = ref(false)
const progressCurrent = ref(0)
const progressTotal = ref(100)
const progressMessage = ref('')

const fileInput = ref(null)

const emit = defineEmits(['upload-complete'])

const stepTitles = [
  'Upload File',
  'Configure Hierarchy',
  'Select Value Column',
  'Name & Create'
]

// Computed properties
const availableColumns = computed(() => {
  const cols = fileInfo.value?.columns || []
  console.log('FileLoaderModal - availableColumns computed:', {
    fileInfoExists: !!fileInfo.value,
    columnsExists: !!fileInfo.value?.columns,
    columnsLength: cols.length,
    columns: cols
  })
  return cols
})

const numericColumns = computed(() => {
  return availableColumns.value.filter(col =>
    col.suitable_for_value && !hierarchyColumns.value.includes(col.name)
  )
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return selectedFile.value !== null
    case 1:
      return hierarchyColumns.value.length >= 3
    case 2:
      return valueColumn.value !== ''
    case 3:
      return chartName.value.trim() !== ''
    default:
      return false
  }
})

const canProcess = computed(() => {
  return chartName.value.trim() !== '' &&
         hierarchyColumns.value.length >= 3 &&
         valueColumn.value !== ''
})

// Methods
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
  statusMessage.value = ''
}

const selectValueColumn = (colName) => {
  valueColumn.value = colName
}

const nextStep = async () => {
  statusMessage.value = ''

  if (currentStep.value === 0 && canProceed.value) {
    // Upload file
    await uploadFile()
  } else if (currentStep.value === 1 && canProceed.value) {
    // Validate hierarchy selection
    currentStep.value++
  } else if (currentStep.value === 2 && canProceed.value) {
    // Move to final step
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
    statusMessage.value = ''
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    statusMessage.value = 'No file selected.'
    statusType.value = 'error'
    return
  }

  try {
    statusMessage.value = 'Uploading file...'
    statusType.value = 'info'

    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetchApi(API_ENDPOINTS.UPLOAD, {
      method: 'POST',
      data: formData
    })

    if (!response?.filePath) {
      throw new Error('No file path returned from upload')
    }

    uploadedFileName.value = response.filePath
    statusMessage.value = 'File uploaded! Analyzing columns...'

    // Fetch file info
    await fetchFileInfo(response.filePath)

    statusMessage.value = ''
    currentStep.value++

  } catch (error) {
    console.error('Upload error:', error)
    statusMessage.value = error.message || 'Upload failed'
    statusType.value = 'error'
  }
}

const fetchFileInfo = async (filePath) => {
  console.log('FileLoaderModal - fetchFileInfo starting, filePath:', filePath)
  isLoadingFileInfo.value = true
  console.log('FileLoaderModal - isLoadingFileInfo set to TRUE')
  try {
    const response = await fetchApi(API_ENDPOINTS.FILE_INFO, {
      method: 'GET',
      params: { filePath }
    })

    console.log('FileLoaderModal - File info received:', response)
    console.log('FileLoaderModal - response type:', typeof response)
    console.log('FileLoaderModal - response is string?:', typeof response === 'string')
    console.log('FileLoaderModal - response keys:', Object.keys(response))
    console.log('FileLoaderModal - response.columns:', response.columns)
    console.log('FileLoaderModal - response["columns"]:', response["columns"])

    // Try parsing if it's a string
    let parsedResponse = response
    if (typeof response === 'string') {
      console.log('FileLoaderModal - Response is a string! Parsing...')
      parsedResponse = JSON.parse(response)
      console.log('FileLoaderModal - Parsed response:', parsedResponse)
    }

    fileInfo.value = parsedResponse
    console.log('FileLoaderModal - fileInfo.value set to:', fileInfo.value)
    console.log('FileLoaderModal - fileInfo.value.columns:', fileInfo.value.columns)

  } catch (error) {
    console.error('Error fetching file info:', error)
    statusMessage.value = 'Failed to analyze file: ' + (error.message || 'Unknown error')
    statusType.value = 'error'
  } finally {
    isLoadingFileInfo.value = false
    console.log('FileLoaderModal - isLoadingFileInfo set to FALSE')
    console.log('FileLoaderModal - currentStep:', currentStep.value)
  }
}

const processFile = async () => {
  if (!canProcess.value) {
    statusMessage.value = 'Please complete all fields before processing.'
    statusType.value = 'error'
    return
  }

  try {
    isProcessing.value = true
    statusMessage.value = 'Creating visualization...'
    statusType.value = 'info'
    progressCurrent.value = 0
    progressTotal.value = 100
    progressMessage.value = 'Starting...'

    // Validate columns first
    const validationResponse = await fetchApi(API_ENDPOINTS.VALIDATE_COLUMNS, {
      method: 'POST',
      data: {
        filePath: uploadedFileName.value,
        treeOrder: hierarchyColumns.value,
        valueColumn: valueColumn.value
      }
    })

    if (!validationResponse.valid) {
      throw new Error('Validation failed: ' + validationResponse.errors.join(', '))
    }

    // Process the file with SSE for progress
    const API_BASE_URL = process.env.VUE_APP_BASE_URL || 'http://localhost:6500'
    const API_PATH = process.env.VUE_APP_API_ROOT_PATH || '/api'

    // Use fetch for SSE instead of EventSource (to support POST with body)
    const response = await fetch(`${API_BASE_URL}${API_PATH}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filePath: uploadedFileName.value,
        chartName: chartName.value,
        treeOrder: hierarchyColumns.value,
        valueColumn: valueColumn.value,
        sessionId: props.sessionId
      })
    })

    if (!response.ok) {
      throw new Error('Processing request failed')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      // Append new chunk to buffer
      buffer += decoder.decode(value, { stream: true })

      // Process complete events (ending with \n\n)
      const events = buffer.split('\n\n')

      // Keep incomplete event in buffer
      buffer = events.pop() || ''

      for (const event of events) {
        if (event.startsWith('data: ')) {
          try {
            const data = JSON.parse(event.substring(6))

            if (data.error) {
              throw new Error(data.error)
            } else if (data.done) {
              progressCurrent.value = 100
              progressTotal.value = 100
              progressMessage.value = 'Complete!'
            } else {
              progressCurrent.value = data.current
              progressTotal.value = data.total
              progressMessage.value = data.message
            }
          } catch (parseError) {
            console.error('Failed to parse SSE event:', event, parseError)
          }
        }
      }
    }

    statusMessage.value = 'Visualization created successfully!'
    statusType.value = 'success'

    await new Promise(resolve => setTimeout(resolve, 1500))
    handleClose()
    emit('upload-complete')

  } catch (error) {
    console.error('Processing error:', error)
    statusMessage.value = error.message || 'Processing failed'
    statusType.value = 'error'
  } finally {
    isProcessing.value = false
    progressCurrent.value = 0
    progressMessage.value = ''
  }
}

const resetForm = () => {
  currentStep.value = 0
  selectedFile.value = null
  uploadedFileName.value = ''
  fileInfo.value = null
  hierarchyColumns.value = []
  valueColumn.value = ''
  chartName.value = ''
  statusMessage.value = ''
  statusType.value = ''
  isProcessing.value = false

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleClose = () => {
  const modalEl = document.getElementById('mdl-load')
  if (modalEl) {
    const modal = bootstrap.Modal.getInstance(modalEl)
    if (modal) {
      modal.hide()
    }
  }
  resetForm()
}

onMounted(() => {
  const modal = document.getElementById('mdl-load')
  modal.addEventListener('show.bs.modal', () => {
    modal.style.display = 'block'
    modal.removeAttribute('aria-hidden')
  })
})
</script>

<style scoped>
.progress-stepper {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  position: relative;
}

.progress-stepper::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 50px;
  right: 50px;
  height: 2px;
  background: #dee2e6;
  z-index: 0;
}

.step {
  flex: 1;
  text-align: center;
  position: relative;
  z-index: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e9ecef;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.5rem;
  font-weight: bold;
  border: 2px solid #dee2e6;
  transition: all 0.3s;
}

.step-title {
  font-size: 0.85rem;
  color: #6c757d;
}

.step.active .step-number {
  background: #0d6efd;
  color: white;
  border-color: #0d6efd;
  transform: scale(1.1);
}

.step.active .step-title {
  color: #0d6efd;
  font-weight: 600;
}

.step.completed .step-number {
  background: #198754;
  color: white;
  border-color: #198754;
}

.step.completed .step-number::after {
  content: '✓';
}

.step-content {
  min-height: 400px;
}

.upload-area {
  padding: 3rem 1rem;
}

.value-option {
  border: 2px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.value-option:hover {
  border-color: #0d6efd;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.value-option.selected {
  border-color: #198754;
  background: #f0fff4;
}

.option-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.option-icon {
  font-size: 1.5rem;
}

.option-name {
  flex: 1;
  font-weight: 500;
}

.config-summary {
  border: 1px solid #dee2e6;
}

.modal-xl {
  max-width: 1000px;
}
</style>
