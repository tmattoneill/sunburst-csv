<template>
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

/* Optional: Add some general styling for the app container */
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin-top: 60px;
}
</style>