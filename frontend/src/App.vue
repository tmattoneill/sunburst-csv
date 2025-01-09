<script>
import SunburstChart from './components/SunburstChart.vue';
import FileLoaderModal from './components/FileLoaderModal.vue';
import DataPane from './components/DataPane.vue';
import PageHeader from './components/PageHeader.vue';

export default {
  name: 'App',
  components: {
    SunburstChart,
    FileLoaderModal,
    DataPane,
    PageHeader,
  },
  data() {
    return {
      chartData: {}, // Initialize as empty object instead of null
      currentPalette: 'ocean',
      reportType: '',
      dateStart: '',
      dateEnd: '',
    };
  },
  async mounted() {
    try {
      const response = await fetch('http://localhost:5001/data');
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const responseData = await response.json();

      // Destructure the response to get all fields
      this.reportType = responseData.report_type;
      this.dateStart = responseData.date_start;
      this.dateEnd = responseData.date_end;
      this.chartData = responseData.data;  // Store just the nested data object

    } catch (error) {
      console.error('Error fetching chart data:', error);
      // Reset all fields on error
      this.reportType = '';
      this.dateStart = '';
      this.dateEnd = '';
      this.chartData = {};
    }
  },
  methods: {
    async handleFileSelected(file) {
      try {
        const text = await file.text();
        // Parse CSV and process data as needed
        console.log('File loaded:', text);

        // For now, we'll just set a dummy data object
        this.data = { /* your data structure */};
      } catch (error) {
        console.error('Error processing file:', error);
        this.data = {};
      }
    }
  },
};
</script>

<template>
  <div id="app" class="container py-4">
    <!-- File Loader Modal -->
    <FileLoaderModal @file-selected="handleFileSelected"/>

    <!-- Main Page -->
    <PageHeader
        :reportType="reportType"
        :chartName="chartData.name"
        :dateStart="dateStart"
        :dateEnd="dateEnd"
    />

    <div class="row">
      <!-- Sunburst Chart Section -->
      <div class="col-md-6 mb-4 mb-md-0">
        <div class="h-100">
          <div v-if="chartData && Object.keys(chartData).length"
               class="d-flex justify-content-center align-items-center"
               style="height: 500px;">
            <SunburstChart
                :chart-data="chartData"
                v-model:palette-name="currentPalette"
            />
          </div>
          <div v-else class="d-flex justify-content-center align-items-center text-secondary fs-5"
               style="height: 500px;">
            <p class="m-0">Loading chart data...</p>
          </div>
        </div>
      </div>

      <!-- Data View Section -->
      <div class="col-md-6">
        <div class="bg-white rounded shadow-sm p-4 h-100">
          <DataPane/>
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