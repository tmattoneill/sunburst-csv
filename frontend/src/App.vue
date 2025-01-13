<!-- App.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import SunburstChart from './components/SunburstChart.vue'
import FileLoaderModal from './components/FileLoaderModal.vue'
import DataPane from './components/DataPane.vue'
import PageHeader from './components/PageHeader.vue'
import DataTable from "@/components/DataTable.vue";

const chartData = ref({})
const currentPalette = ref('Ocean')
const reportType = ref('')
const dateStart = ref('')
const dateEnd = ref('')
const selectedNode = ref(null)
const currentPath = ref([])

// Computed properties for DataPane
const rootName = computed(() => selectedNode.value?.name ?? chartData.value?.name ?? '')
const rootValue = computed(() => selectedNode.value?.value ?? chartData.value?.value ?? 0)
const topChildren = computed(() => selectedNode.value?.children ?? chartData.value?.children ?? [])
const chartName = computed(() => chartData.value?.name ?? '')

// Add handler for node selection
const handleNodeClick = (node) => {
  selectedNode.value = node
}

const handleNodeHover = (node) => {
  selectedNode.value = node || chartData.value;
}

const handlePathChange = (path) => {
  console.log('Path change in App:', path);
  currentPath.value = path;
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

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:5001/data')
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    const responseData = await response.json()

    reportType.value = responseData.report_type
    dateStart.value = responseData.date_start
    dateEnd.value = responseData.date_end
    chartData.value = responseData.data
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
})

const refreshPage = () => {
  location.reload()
}
</script>

<template>
  <FileLoaderModal @file-selected="handleFileSelected"/>

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
              :chart-data="chartData"
              v-model:palette-name="currentPalette"
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
        <DataTable />
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