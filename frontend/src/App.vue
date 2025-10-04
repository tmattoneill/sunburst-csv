<!-- App.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import SunburstChart from './components/SunburstChart.vue'
import FileLoaderModal from './components/FileLoaderModal.vue'
import DataPane from './components/DataPane.vue'
import PageHeader from './components/PageHeader.vue'
import DataTable from "@/components/DataTable.vue";
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
const valueColumn = ref('') // Generic mode: name of the value column
const selectedNode = ref(null)
const hoveredNode = ref(null);
const currentPath = ref([])
const currentFilters = ref({}) // for the data table
const chartRef = ref(null)
const filterOrder = ref([])
const isLoadingData = ref(false)

// Computed properties for DataPane
const dataPaneNode = computed(() => hoveredNode.value || selectedNode.value);
const rootName = computed(() => dataPaneNode.value?.name || chartData.value?.name || '');
const rootValue = computed(() => dataPaneNode.value?.value || chartData.value?.value || 0);
const topChildren = computed(() => dataPaneNode.value?.children || chartData.value?.children || []);


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
  console.log('Path change in App:', path);
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
    }

    chartData.value = responseData.data
    filterOrder.value = treeOrder.value
    selectedNode.value = responseData.data
    currentPath.value = [{ name: responseData.data.name, value: responseData.data.value }]
  } catch (error) {
    console.error('Error fetching chart data:', error)
    reportType.value = ''
    chartName.value = ''
    dateStart.value = ''
    dateEnd.value = ''
    treeOrder.value = []
    chartData.value = {}
    selectedNode.value = null
    currentPath.value = []
  } finally {
    isLoadingData.value = false
  }
}

onMounted(async () => {
  await fetchData()

  // If no data loaded or data is empty, automatically open the upload modal
  const hasData = chartData.value &&
                  Object.keys(chartData.value).length > 0 &&
                  chartData.value.name

  if (!hasData) {
    // Wait a moment for the modal to be registered in the DOM
    setTimeout(() => {
      const modalEl = document.getElementById('mdl-load')
      if (modalEl && window.bootstrap) {
        const modal = new window.bootstrap.Modal(modalEl)
        modal.show()
      }
    }, 500)
  }
})

const refreshPage = () => {
  fetchData(true)  // Show loading overlay when explicitly refreshing
}
</script>

<template>
  <div>
    <!-- Loading Overlay -->
    <div v-if="isLoadingData" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
          <span class="visually-hidden">Loading...</span>
        </div>
        <h4 class="mb-2">Processing Dataset</h4>
        <p class="text-muted">This may take a moment for large files...</p>
      </div>
    </div>

    <FileLoaderModal
      :session-id="sessionId"
      @file-selected="handleFileSelected"
      @upload-complete="refreshPage"
    />

    <div id="app" class="container py-4">
    <!-- Header -->
  <PageHeader
    :reportType="reportType"
    :chartName="chartName"
    :dateStart="dateStart"
    :dateEnd="dateEnd"
    :treeOrder="treeOrder"
    :paletteName="currentPalette"
    :currentPath="currentPath"
    @update:paletteName="(name) => currentPalette = name"
    @navigate-to="handlePathNavigation"
  />

    <div class="row">
      <div class="col-md-6 mb-4 mb-md-0">
        <!-- Chart Pane -->
        <div class="h-100 position-relative">
          <div
            v-if="chartData && Object.keys(chartData).length"
            class="d-flex justify-content-center align-items-center"
            style="height: 500px;"
          >
            <SunburstChart
              ref="chartRef"
              :chart-data="chartData"
              :palette-name="currentPalette"
              @update:palette-name="(name) => currentPalette = name"
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
      <div class="col-md-6">
        <!-- Data Pane -->
        <div class="bg-black rounded shadow-sm p-4 h-100">
          <DataPane
            :rootName="rootName"
            :rootValue="rootValue"
            :topChildren="topChildren"
            :valueColumn="valueColumn"
          />
        </div>
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-12">
        <!-- DataTable Component - Updates Dynamically -->
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
</template>

<style scoped>
#app {
  max-width: 1200px;
  background: #f8f9fa;
  border-radius: 8px;
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
</style>