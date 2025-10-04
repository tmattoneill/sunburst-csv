<!-- App.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import SunburstChart from './components/SunburstChart.vue'
import FileLoaderModal from './components/FileLoaderModal.vue'
import DataPane from './components/DataPane.vue'
import PageHeader from './components/PageHeader.vue'
import DataTable from "@/components/DataTable.vue";
import { fetchApi, API_ENDPOINTS } from '@/services/api';

const chartData = ref({})
const currentPalette = ref('Ocean')
const reportType = ref('')
const dateStart = ref('')
const dateEnd = ref('')
const selectedNode = ref(null)
const hoveredNode = ref(null);
const currentPath = ref([])
const currentFilters = ref({}) // for the data table
const chartRef = ref(null)
const filterOrder = ref([])

// Computed properties for DataPane
const dataPaneNode = computed(() => hoveredNode.value || selectedNode.value);
const rootName = computed(() => dataPaneNode.value?.name || chartData.value?.name || '');
const rootValue = computed(() => dataPaneNode.value?.value || chartData.value?.value || 0);
const topChildren = computed(() => dataPaneNode.value?.children || chartData.value?.children || []);
const chartName = computed(() => chartData.value?.name ?? '')


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


const fetchData = async () => {
  try {
    const responseData = await fetchApi(API_ENDPOINTS.DATA)

    reportType.value = responseData.report_type
    dateStart.value = responseData.date_start
    dateEnd.value = responseData.date_end
    chartData.value = responseData.data
    filterOrder.value = responseData.tree_order
    selectedNode.value = responseData.data
    currentPath.value = [{ name: responseData.data.name, value: responseData.data.value }]
  } catch (error) {
    console.error('Error fetching chart data:', error)
    reportType.value = ''
    dateStart.value = ''
    dateEnd.value = ''
    chartData.value = {}
    selectedNode.value = null
    currentPath.value = []
  }
}

onMounted(() => {
  fetchData()
})

const refreshPage = () => {
  fetchData()
}
</script>

<template>
  <div>
    <FileLoaderModal
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
          />
        </div>
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-12">
        <!-- DataTable Component - Updates Dynamically -->
        <DataTable
          :filters="currentFilters"
          :rootName="chartName"
          :dateStart="dateStart"
          :dateEnd="dateEnd"
          :currentNodeName="rootName"
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
</style>