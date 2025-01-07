<script>
import SunburstChart from './components/SunburstChart.vue';
import FileLoaderModal from './components/FileLoaderModal.vue';
import DataPane from './components/DataPane.vue';

export default {
  name: 'App',
  components: {
    SunburstChart,
    FileLoaderModal,
    DataPane,
  },
  data() {
    return {
      data: {}, // Initialize as empty object instead of null
      currentPalette: 'ocean',
    };
  },
  async mounted() {
    try {
      const response = await fetch('http://localhost:5001/data');
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      this.data = await response.json();
    } catch (error) {
      console.error('Error fetching chart data:', error);
      this.data = {}; // Fallback to empty object
    }
  },
  methods: {
    async handleFileSelected(file) {
      try {
        const text = await file.text();
        // Parse CSV and process data as needed
        console.log('File loaded:', text);

        // For now, we'll just set a dummy data object
        this.data = { /* your data structure */ };
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
    <FileLoaderModal @file-selected="handleFileSelected" />

    <!-- Main Page -->
    <div class="row mb-4">
      <div class="col-12">
        <button
            class="btn btn-primary px-4"
            id="mdl-btn-load"
            type="button"
            data-bs-toggle="modal"
            data-bs-target="#mdl-load"
        >
          Load Data
        </button>
      </div>
    </div>

    <div class="row">
      <!-- Sunburst Chart Section -->
      <div class="col-md-6 mb-4 mb-md-0">
        <div class="h-100">
          <div v-if="data && Object.keys(data).length" class="d-flex justify-content-center align-items-center"
               style="height: 500px;">
            <SunburstChart
                :chart-data="data"
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
          <DataPane />
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