<template>
  <div id="app">
    <!-- File Loader Modal -->
    <FileLoaderModal @file-selected="handleFileSelected" />

    <!-- Main Page -->
    <div id="div-main-page">
      <div class="container">
        <div class="row">
          <div class="col">
            <div class="px-9 py-2">
              <div class="container">
                <button
                    class="btn btn-primary"
                    id="mdl-btn-load"
                    type="button"
                    data-bs-toggle="modal"
                    data-bs-target="#mdl-load"
                >
                  Load Data
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="container">
        <div class="row">
          <!-- Sunburst Chart Section -->
          <div class="col-md-6">
            <div id="div-chart">
              <div v-if="data && Object.keys(data).length" class="chart-container">
                <SunburstChart
                    :chart-data="data"
                    v-model:palette-name="currentPalette"
                />
              </div>
              <div v-else class="loading-message">
                <p>Loading chart data...</p>
              </div>
            </div>
          </div>

          <!-- Data View Section -->
          <div class="col-md-6">
            <div id="div-data-view">
              <div id="div-current-root">
                <h1>Root Value</h1>
              </div>
              <div id="div-child-data">
                <ul>
                  <li v-for="(value, index) in childData" :key="index">
                    {{ value }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SunburstChart from './components/SunburstChart.vue';
import FileLoaderModal from './components/FileLoaderModal.vue';

export default {
  name: 'App',
  components: {
    SunburstChart,
    FileLoaderModal,
  },
  data() {
    return {
      data: {}, // Initialize as empty object instead of null
      currentPalette: 'ocean',
      childData: [
        'Malware Type 1: 245',
        'Malware Type 2: 189',
        'Malware Type 3: 133',
        'Malware Type 4: 101',
      ],
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
        // You might want to use a CSV parsing library here
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

<style>
#app {
  font-family: 'Roboto', Arial, sans-serif;
  margin: 20px auto;
  max-width: 1200px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.chart-container {
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
}

#div-data-view {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
  height: 100%;
}

#div-child-data ul {
  list-style: none;
  padding: 0;
}

#div-child-data ul li {
  padding: 8px 0;
  font-size: 1rem;
  color: #555;
}

.loading-message {
  font-size: 1.2rem;
  color: #555;
  text-align: center;
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn-primary {
  margin: 0 auto;
  font-size: 1.2rem;
  padding: 10px 20px;
}
</style>