<script setup>
const emit = defineEmits(['launch-app'])

const handleLaunch = () => {
  emit('launch-app')
}
</script>

<template>
  <div class="landing-page">
    <section class="hero text-center py-5">
      <div class="container">
        <span class="badge rounded-pill bg-primary-subtle text-primary fw-semibold mb-3">Sunburst CSV</span>
        <h1 class="display-5 fw-bold text-dark mb-3">Turn hierarchical CSVs into explorable sunburst charts</h1>
        <p class="lead text-muted mx-auto hero-lead">
          Upload multi-level datasets, configure your hierarchy, and share interactive charts that surface the stories inside your data.
        </p>
        <button class="btn btn-primary btn-lg px-4 mt-4" @click="handleLaunch">
          Launch App
        </button>
        <p class="text-muted small mt-3">Runs locally in your browser — data stays with your session.</p>
      </div>
    </section>

    <section class="py-5 bg-white">
      <div class="container">
        <div class="row g-4 align-items-stretch">
          <div class="col-md-4">
            <div class="feature-card h-100 shadow-sm p-4">
              <span class="feature-icon text-primary mb-3"><i class="bi bi-diagram-3"></i></span>
              <h3 class="h5 fw-semibold">Guided upload flow</h3>
              <p class="text-muted mb-0">Step-by-step wizard validates your columns, keeps values in sync, and previews your hierarchy before charting.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card h-100 shadow-sm p-4">
              <span class="feature-icon text-primary mb-3"><i class="bi bi-bar-chart"></i></span>
              <h3 class="h5 fw-semibold">Interactive exploration</h3>
              <p class="text-muted mb-0">Drill down by clicking segments, compare categories on hover, and stay oriented with dynamic breadcrumbs.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card h-100 shadow-sm p-4">
              <span class="feature-icon text-primary mb-3"><i class="bi bi-table"></i></span>
              <h3 class="h5 fw-semibold">Linked data tables</h3>
              <p class="text-muted mb-0">Filter raw rows to match the current slice, export subsets, and keep numeric formatting intact.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5 bg-light">
      <div class="container">
        <div class="row g-4">
          <div class="col-lg-6">
            <h2 class="h4 fw-bold mb-3">How to get started</h2>
            <ul class="list-group list-group-flush steps-list">
              <li class="list-group-item">
                <strong>1. Prepare your file:</strong> Use CSV or Excel with 3+ categorical columns and at least one numeric column to aggregate.
              </li>
              <li class="list-group-item">
                <strong>2. Configure the hierarchy:</strong> Order your columns from broad to specific (e.g., Region → Country → Product).
              </li>
              <li class="list-group-item">
                <strong>3. Explore and share:</strong> Drill into the chart, review the linked table, and export filtered results as needed.
              </li>
            </ul>
          </div>
          <div class="col-lg-6">
            <h2 class="h4 fw-bold mb-3">Dataset best practices</h2>
            <div class="best-practices p-4 rounded">
              <ul class="mb-0 text-muted">
                <li>Keep column headers concise (Title Case or snake_case) and avoid merged cells.</li>
                <li>Ensure numeric columns contain clean numbers (currency symbols are OK; we parse them).</li>
                <li>Limit hierarchy depth to 3-6 levels for optimal readability.</li>
                <li>Group low-volume categories into an "Other" row to reduce noise.</li>
                <li>Test with the sample files in <code>data_samples/</code> to confirm formatting before uploading sensitive data.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5 cta-section text-center">
      <div class="container">
        <h2 class="h4 fw-bold text-dark mb-3">Ready to build your sunburst?</h2>
        <p class="text-muted mb-4">Upload your dataset to uncover structure, impact, and outliers in minutes.</p>
        <button class="btn btn-primary btn-lg px-4" @click="handleLaunch">Launch App</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.landing-page {
  font-family: 'Roboto', sans-serif;
  background: linear-gradient(180deg, #f5f9ff 0%, #ffffff 40%);
  color: #1f2933;
}

.hero {
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.08), rgba(15, 118, 110, 0.05));
}

.hero .hero-lead {
  max-width: 640px;
}

.feature-card {
  border-radius: 16px;
  background: #ffffff;
}

.feature-icon {
  font-size: 1.75rem;
}

.steps-list .list-group-item {
  background: transparent;
  border: none;
  padding-left: 0;
}

.best-practices {
  background: rgba(13, 110, 253, 0.08);
  border: 1px solid rgba(13, 110, 253, 0.12);
}

.cta-section {
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.12), rgba(15, 118, 110, 0.08));
}

button.btn-primary {
  box-shadow: 0 12px 24px rgba(13, 110, 253, 0.25);
}

@media (max-width: 767px) {
  .hero h1 {
    font-size: 2rem;
  }

  .feature-card {
    text-align: left;
  }
}
</style>
