<template>
  <h1>Sunburst Chart</h1>
  <div class="app">
    <SunburstChart
        :chart-data="data"
        v-model:palette-name="currentPalette"
    />
  </div>
</template>

<script>
import SunburstChart from './components/SunburstChart.vue';

export default {
  name: 'App',
  components: {
    SunburstChart
  },
  data() {
    return {
      data: {},
      currentPalette: 'ocean'
    };
  },
  async mounted() {
    try {
      const response = await fetch('http://localhost:5001/data');
      this.data = await response.json();
    } catch (error) {
      console.error('Error fetching chart data:', error);
    }
  }
};
</script>

<style>
.app {
  height: 500px;
}

/* general styling for the app container */
#app {
  font-family: 'Roboto', Arial, sans-serif; /* Use a modern font */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin: 60px auto; /* Centered and with some top margin */
  max-width: 800px; /* Limit the width for better readability */
  padding: 20px; /* Add padding inside the container */
  background: linear-gradient(135deg, #f8f9fa, #e9ecef); /* Soft gradient background */
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
  border-radius: 8px; /* Smooth rounded corners */
  color: #333; /* Default text color */
}

/* Optional styling for headers within the container */
#app h1, #app h2, #app h3 {
  color: #2c3e50; /* Darker color for contrast */
  margin-bottom: 10px;
  font-weight: 600; /* Bold and prominent */
}

/* Style links to make them stand out */
#app a {
  color: #007bff; /* Blue link color */
  text-decoration: none;
  transition: color 0.2s ease-in-out;
}
</style>