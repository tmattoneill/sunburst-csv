<!-- App.vue -->
<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import SunburstChart from './components/SunburstChart.vue'
import FileLoaderModal from './components/FileLoaderModal.vue'
import DataPane from './components/DataPane.vue'
import PageHeader from './components/PageHeader.vue'
import LandingPage from './components/LandingPage.vue'
import SidebarControls from './components/SidebarControls.vue'
import DataTable from "@/components/DataTable.vue";
import { PALETTES } from '@/palettes'
import { fetchApi, API_ENDPOINTS } from '@/services/api';

// Session management
const getOrCreateSessionId = () => {
  let sessionId = localStorage.getItem('sunburst_session_id')
  if (!sessionId) {
    sessionId = Date.now().toString(36) + Math.random().toString(36).substring(2)
    localStorage.setItem('sunburst_session_id', sessionId)
  }
  return sessionId
}

const sessionId = ref(getOrCreateSessionId())

const chartData = ref({})
const currentPalette = ref('Ocean')
const reportType = ref('')
const chartName = ref('')
const dateStart = ref('')
const dateEnd = ref('')
const treeOrder = ref([])
const pendingTreeOrder = ref([])
const valueColumn = ref('') // Generic mode: name of the value column
const selectedNode = ref(null)
const hoveredNode = ref(null);
const currentPath = ref([])
const currentFilters = ref({}) // for the data table
const chartRef = ref(null)
const filterOrder = ref([])
const isLoadingData = ref(false)
const loadingMessage = ref('Processing dataset...')
const isInitialLoad = ref(true); // Controls the initial overlay
const showLanding = ref(true)
const hasLaunched = ref(false)
const aggregationMode = ref('')
const originalLeafRecords = ref([])

const paletteOptions = computed(() => Object.keys(PALETTES))

// Computed properties for DataPane
const dataPaneNode = computed(() => hoveredNode.value || selectedNode.value);
const rootName = computed(() => dataPaneNode.value?.name || chartData.value?.name || '');
const rootValue = computed(() => dataPaneNode.value?.value || chartData.value?.value || 0);
const topChildren = computed(() => dataPaneNode.value?.children || chartData.value?.children || []);
const hasChartData = computed(() => chartData.value && Object.keys(chartData.value).length > 0)

const extractLeafRecords = (root, order) => {
  if (!root || !Array.isArray(order)) return []

  const records = []

  const traverse = (node, depth, record) => {
    if (!node || typeof node !== 'object') {
      return
    }

    const children = Array.isArray(node.children) ? node.children : []

    if (!children.length) {
      records.push({
        fields: { ...record },
        value: Number(node.value) || 0
      })
      return
    }

    children.forEach(child => {
      const columnName = order[depth] || `Level ${depth + 1}`
      const nextRecord = { ...record }
      if (columnName) {
        nextRecord[columnName] = child.name
      }
      traverse(child, depth + 1, nextRecord)
    })
  }

  traverse(root, 0, {})
  return records
}

watch(treeOrder, (order) => {
  pendingTreeOrder.value = Array.isArray(order) ? [...order] : []
}, { immediate: true })

const buildTreeFromRecords = (records, order, rootLabel) => {
  const root = {
    name: rootLabel || 'Visualization',
    value: 0,
    children: []
  }

  const addPath = (path, value) => {
    root.value += value
    let current = root

    path.forEach(segment => {
      if (!segment) {
        return
      }
      let child = current.children.find(c => c.name === segment)
      if (!child) {
        child = { name: segment, value: 0, children: [] }
        current.children.push(child)
      }
      child.value += value
      current = child
    })
  }

  records.forEach(record => {
    const path = order
      .map(column => record.fields[column])
      .filter(segment => segment !== undefined && segment !== null)

    if (path.length === 0) {
      // Fall back to any remaining fields
      const fallbackPath = Object.values(record.fields)
      if (fallbackPath.length) {
        addPath(fallbackPath, record.value)
      } else {
        root.value += record.value
      }
      return
    }

    addPath(path, record.value)
  })

  const sortTree = (node) => {
    if (!node.children) return
    node.children.sort((a, b) => (b.value || 0) - (a.value || 0))
    node.children.forEach(sortTree)
  }

  sortTree(root)
  return root
}

// Add handler for node selection
const handleNodeClick = (node) => {
  selectedNode.value = node;
  hoveredNode.value = null; // Clear hover so DataPane sticks to the clicked node when not hovering
  if (node.children) {
    chartRef.value?.updateChart(node);
  }
}


const handleNodeHover = (node) => {
  // Simply update hoveredNode on hover; do not affect selectedNode
  hoveredNode.value = node;
}

const handlePathChange = (path) => {
  currentPath.value = path;

  // Build filters from path
  const filters = {};

  path.forEach((node, index) => {
    if (index > 0) { // Skip root node
      filters[filterOrder.value[index - 1]] = node.name;
    }
  });

  currentFilters.value = filters;
}

const handleFileSelected = async (file) => {
  try {
    const text = await file.text()
    console.log('File loaded:', text)
    // For now, we'll just set a dummy data object
    chartData.value = { /* your data structure */ }
  } catch (error) {
    console.error('Error processing file:', error)
    chartData.value = {}
  }
}

const handlePathNavigation = ({ segment, index }) => {
  // Walk the tree to find the target node
  let targetNode = chartData.value; // Start at the root
  const path = currentPath.value.slice(0, index + 1);

  // Navigate from the root to the target level
  for (let i = 1; i <= index; i++) {
    const segmentId = path[i].id;
    targetNode = targetNode.children.find(child => child.nodeId === segmentId);
  }

  selectedNode.value = targetNode;

  // Update currentPath and recalc filters
  handlePathChange(path);

  // Optionally update the chart with the target node
  if (targetNode) {
    handleNodeClick(targetNode);
  }
};


const fetchData = async (showLoading = false) => {
  try {
    if (showLoading) {
      isLoadingData.value = true
    }
    const responseData = await fetchApi(API_ENDPOINTS.DATA, {
      method: 'GET',
      params: { session_id: sessionId.value }
    })

    // Support both legacy and generic metadata formats
    if (responseData.chart_name) {
      // Generic mode
      chartName.value = responseData.chart_name
      treeOrder.value = responseData.tree_order || []
      valueColumn.value = responseData.value_column || ''
      aggregationMode.value = responseData.aggregation_mode || (valueColumn.value ? 'SUM' : 'COUNT_TOTAL')
      reportType.value = ''
      dateStart.value = ''
      dateEnd.value = ''
    } else {
      // Legacy mode (security reports)
      chartName.value = responseData.data?.name || 'Chart'
      reportType.value = responseData.report_type || ''
      dateStart.value = responseData.date_start || ''
      dateEnd.value = responseData.date_end || ''
      treeOrder.value = responseData.tree_order || []
      valueColumn.value = '' // No value column in legacy mode
      aggregationMode.value = responseData.aggregation_mode || ''
    }

    chartData.value = responseData.data
    filterOrder.value = Array.isArray(treeOrder.value) ? [...treeOrder.value] : []
    selectedNode.value = responseData.data
    currentPath.value = [{ name: responseData.data.name, value: responseData.data.value }]

    if (responseData.data) {
      originalLeafRecords.value = extractLeafRecords(responseData.data, treeOrder.value)
    } else {
      originalLeafRecords.value = []
    }
  } catch (error) {
    // Only log error if it's not a 404 (which is expected on initial load with no data)
    if (!error.message.includes('404') && !error.message.includes('Data file not found')) {
      console.error('Error fetching chart data:', error)
    }
    reportType.value = ''
    chartName.value = ''
    dateStart.value = ''
    dateEnd.value = ''
    treeOrder.value = []
    chartData.value = {}
    selectedNode.value = null
    currentPath.value = []
    aggregationMode.value = ''
    originalLeafRecords.value = []
  } finally {
    isLoadingData.value = false
  }
}

const showUploadModal = (delay = 300) => {
  if (typeof window === 'undefined') {
    return
  }

  setTimeout(() => {
    const modalEl = document.getElementById('mdl-load')
    if (modalEl && window.bootstrap) {
      const modalInstance = window.bootstrap.Modal.getOrCreateInstance(modalEl)
      modalInstance.show()
    }
  }, delay)
}

const initializeApp = async () => {
  await fetchData(true)

  const hasData = chartData.value &&
                  Object.keys(chartData.value).length > 0 &&
                  chartData.value.name

  if (hasData) {
    isInitialLoad.value = false
  } else {
    showUploadModal(500)
  }
}

const launchApp = async () => {
  if (!showLanding.value) {
    return
  }

  showLanding.value = false

  if (typeof window !== 'undefined') {
    const url = new URL(window.location.href)
    url.searchParams.set('app', '1')
    window.history.replaceState({}, '', url)
  }

  if (hasLaunched.value) {
    return
  }

  hasLaunched.value = true
  await nextTick()
  await initializeApp()
}

onMounted(() => {
  if (typeof window === 'undefined') {
    return
  }

  const params = new URLSearchParams(window.location.search)
  const shouldAutoLaunch = params.get('app') === '1' || params.get('launch') === '1' || window.location.hash === '#app'

  if (shouldAutoLaunch) {
    launchApp()
  }
})

const refreshPage = () => {
  if (showLanding.value) {
    return
  }
  isInitialLoad.value = false;
  fetchData(true)  // Show loading overlay when explicitly refreshing
}

// Handle new upload - shows confirmation modal first
const showClearConfirmModal = ref(false)

const handleNewUpload = () => {
  showClearConfirmModal.value = true
}

const cancelClearSession = () => {
  showClearConfirmModal.value = false
}

const confirmClearSession = async () => {
  try {
    // Close confirmation modal
    showClearConfirmModal.value = false

    // Call clear-session endpoint
    await fetchApi(API_ENDPOINTS.CLEAR_SESSION, {
      method: 'POST',
      data: { session_id: sessionId.value }
    })

    // Reset local state
    chartData.value = {}
    selectedNode.value = null
    currentPath.value = []
    currentFilters.value = {}
    chartName.value = ''
    treeOrder.value = []
    valueColumn.value = ''
    aggregationMode.value = ''

    // Wait a moment, then open the upload modal
    showUploadModal()
  } catch (error) {
    console.error('Error clearing session:', error)
    alert('Failed to clear session data: ' + error.message)
  }
}

const handleProcessingStart = () => {
  isLoadingData.value = true
  loadingMessage.value = 'Starting...'
}

const handleProcessingProgress = (message) => {
  loadingMessage.value = message
}

const handleProcessingComplete = () => {
  loadingMessage.value = 'Loading visualization...'
}

const handleDraftTreeOrderUpdate = (order) => {
  pendingTreeOrder.value = Array.isArray(order) ? [...order] : []
}

const handlePaletteUpdate = (palette) => {
  currentPalette.value = palette
}

const resetSelectionState = (root) => {
  if (!root) {
    selectedNode.value = null
    currentPath.value = []
    currentFilters.value = {}
    return
  }
  selectedNode.value = root
  currentPath.value = [{ name: root.name, value: root.value }]
  currentFilters.value = {}
}

const handleSidebarRefresh = () => {
  if (!pendingTreeOrder.value.length) {
    return
  }

  treeOrder.value = [...pendingTreeOrder.value]
  filterOrder.value = [...pendingTreeOrder.value]

  if (originalLeafRecords.value.length) {
    const newTree = buildTreeFromRecords(
      originalLeafRecords.value,
      treeOrder.value,
      chartName.value || chartData.value?.name || 'Visualization'
    )

    chartData.value = newTree
    resetSelectionState(newTree)
    isInitialLoad.value = false
    chartRef.value?.updateChart(newTree)
  } else {
    // Fall back to refetching data if we have no record snapshot
    fetchData(true)
  }
}
</script>

<template>
  <div class="app-shell">
    <LandingPage v-if="showLanding" @launch-app="launchApp" />
    <div v-else class="app-surface">
      <div v-if="isLoadingData" class="loading-overlay">
        <div class="loading-content">
          <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h4 class="mb-2">Processing Dataset</h4>
          <p class="text-primary fw-bold loading-message">{{ loadingMessage }}</p>
        </div>
      </div>

      <div v-if="showClearConfirmModal" class="modal-backdrop fade show"></div>
      <div v-if="showClearConfirmModal" class="modal fade show d-block" tabindex="-1" role="dialog">
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Clear Current Visualization?</h5>
              <button type="button" class="btn-close" @click="cancelClearSession" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <p>This will delete all data for the current visualization.</p>
              <p class="mb-0 text-muted">Are you sure you want to continue?</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="cancelClearSession">Cancel</button>
              <button type="button" class="btn btn-danger" @click="confirmClearSession">OK</button>
            </div>
          </div>
        </div>
      </div>

      <FileLoaderModal
        :session-id="sessionId"
        @file-selected="handleFileSelected"
        @upload-complete="refreshPage"
        @processing-progress="handleProcessingProgress"
        @processing-start="handleProcessingStart"
        @processing-complete="handleProcessingComplete"
      />
      <div class="container py-4">
        <div class="row g-4">
          <div class="col-lg-3">
            <SidebarControls
              :chart-name="chartName"
              :aggregation-mode="aggregationMode"
              :value-column="valueColumn"
              :tree-order="pendingTreeOrder"
              :active-tree-order="treeOrder"
              :palette-name="currentPalette"
              :palette-options="paletteOptions"
              :has-data="hasChartData"
              @update:treeOrder="handleDraftTreeOrderUpdate"
              @update:paletteName="handlePaletteUpdate"
              @refresh="handleSidebarRefresh"
              @new-upload="handleNewUpload"
            />
          </div>
          <div class="col-lg-9">
            <div class="visualization-panel py-4" :class="{ 'initial-load-overlay': isInitialLoad }">
              <PageHeader
                :reportType="reportType"
                :chartName="chartName"
                :dateStart="dateStart"
                :dateEnd="dateEnd"
                :treeOrder="treeOrder"
                :currentPath="currentPath"
                @navigate-to="handlePathNavigation"
              />

              <div class="row">
                <div class="col-lg-6 mb-4 mb-lg-0">
                  <div class="h-100 position-relative">
                    <div
                      v-if="hasChartData"
                      class="d-flex justify-content-center align-items-center"
                      style="height: 500px;"
                    >
                      <SunburstChart
                        ref="chartRef"
                        :chart-data="chartData"
                        :palette-name="currentPalette"
                        @node-click="handleNodeClick"
                        @node-hover="handleNodeHover"
                        @path-change="handlePathChange"
                      />
                      <button
                        class="btn btn-secondary position-absolute"
                        style="bottom: 10px; right: 10px;"
                        @click="refreshPage"
                        title="Refresh Data"
                      >
                        <i class="bi bi-arrow-clockwise"></i>
                      </button>
                    </div>
                    <div
                      v-else
                      class="d-flex justify-content-center align-items-center text-secondary fs-5"
                      style="height: 500px;"
                    >
                      <p class="m-0">Loading chart data...</p>
                    </div>
                  </div>
                </div>
                <div class="col-lg-6">
                  <div class="bg-black rounded shadow-sm p-4 h-100">
                    <DataPane
                      :rootName="rootName"
                      :rootValue="rootValue"
                      :topChildren="topChildren"
                      :valueColumn="valueColumn"
                      :aggregationMode="aggregationMode"
                      :treeOrder="treeOrder"
                    />
                  </div>
                </div>
              </div>

              <div class="row mt-4">
                <div class="col-12">
                  <DataTable
                    :session-id="sessionId"
                    :filters="currentFilters"
                    :rootName="chartName"
                    :dateStart="dateStart"
                    :dateEnd="dateEnd"
                    :currentNodeName="rootName"
                    :treeOrder="treeOrder"
                    :valueColumn="valueColumn"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: linear-gradient(180deg, #f1f5f9 0%, #ffffff 100%);
}

.app-surface {
  padding: 3rem 0;
}

.visualization-panel {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
}

.visualization-panel.initial-load-overlay {
  position: relative;
  pointer-events: none; /* Disables clicks on the content behind the overlay */
}

.visualization-panel.initial-load-overlay::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.95); /* A strong white overlay to hide content */
  z-index: 1041; /* Position it below the modal (z-index 1050+) but above the page content */
}


@media (max-width: 768px) {
  .chart-height {
    height: 400px;
  }
}

.btn {
  z-index: 10;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content {
  background: white;
  padding: 3rem 4rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.loading-content h4 {
  color: #333;
  font-weight: 600;
}

.loading-content p {
  margin: 0;
  font-size: 0.95rem;
}

.loading-message {
  font-size: 1rem;
  min-height: 1.5rem;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
