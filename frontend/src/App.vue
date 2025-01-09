<!-- App.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import SunburstChart from './components/SunburstChart.vue'
import FileLoaderModal from './components/FileLoaderModal.vue'
import DataPane from './components/DataPane.vue'
import PageHeader from './components/PageHeader.vue'

const chartData = ref({})
const currentPalette = ref('ocean')
const reportType = ref('')
const dateStart = ref('')
const dateEnd = ref('')

// Computed properties for DataPane
const rootName = computed(() => chartData.value?.name ?? '')
const rootValue = computed(() => chartData.value?.value ?? 0)
const topChildren = computed(() => chartData.value?.children ?? [])

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
  } catch (error) {
    console.error('Error fetching chart data:', error)
    reportType.value = ''
    dateStart.value = ''
    dateEnd.value = ''
    chartData.value = {}
  }
})
</script>

<template>
  <FileLoaderModal @file-selected="handleFileSelected"/>

  <div id="app" class="container py-4">
    <PageHeader
        :reportType="reportType"
        :chartName="chartData.name"
        :dateStart="dateStart"
        :dateEnd="dateEnd"
    />

    <div class="row">
      <div class="col-md-6 mb-4 mb-md-0">
        <div class="h-100">
          <div
              v-if="chartData && Object.keys(chartData).length"
              class="d-flex justify-content-center align-items-center"
              style="height: 500px;"
          >
            <SunburstChart
                :chart-data="chartData"
                v-model:palette-name="currentPalette"
            />
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
        <div class="bg-white rounded shadow-sm p-4 h-100">
          <DataPane
              :rootName="rootName"
              :rootValue="rootValue"
              :topChildren="topChildren"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
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
</style>