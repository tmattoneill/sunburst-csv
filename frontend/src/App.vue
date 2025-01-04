<template>
  <div style="width: 800px; height: 600px">
    <SunburstChart :chartData="chartData" v-if="chartData" />
  </div>
  <button @click="processData">Reprocess Data</button>
</template>

<script>
import SunburstChart from './components/SunburstChart.vue';

export default {
  components: {
    SunburstChart,
  },
  data() {
    return {
      chartData: null,
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    processData(){
      this.fetchData()
    },
    async fetchData() {
      try {
        const response = await fetch('http://127.0.0.1:5001/data');
        if (!response.ok) {
          const message = `An error has occurred: ${response.status} from backend`;
          throw new Error(message);
        }
        this.chartData = await response.json();

      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
  },
};
</script>