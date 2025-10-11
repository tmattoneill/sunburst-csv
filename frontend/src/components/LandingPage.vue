<!-- frontend/src/components/LandingPage.vue -->
<template>
  <div class="landing-container">
    <div class="landing-content">
      <h1 class="display-4">Welcome to Sunchart</h1>
      <p class="lead">
        An interactive data visualization tool designed to bring your hierarchical data to life.
        Explore complex datasets with intuitive sunburst charts, dynamic tables, and powerful filtering.
      </p>
      <hr class="my-4">
      <p>
        Ready to get started? Upload your CSV or Excel file to begin your analysis.
      </p>
      <button class="btn btn-primary btn-lg" @click="$emit('open-modal')">
        Start Analysis
      </button>
    </div>
  </div>
</template>

<script setup>
  defineEmits(['open-modal']);
</script>

<style scoped>
  .landing-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    text-align: center;
    background-color: #f8f9fa;
  }
  .landing-content {
    max-width: 600px;
    padding: 2rem;
  }
</style>
