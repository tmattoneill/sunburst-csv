<template>
  <div class="row mb-4">
    <div class="col-12 position-relative">
      <div class="mb-4">
        <h3>{{ reportType }}: {{ chartName }}</h3>

        <div class="mt-3 ps-2 d-flex justify-content-between align-items-end">
          <div>
            <h5 class="mb-1">From: {{ dateStart }}</h5>
            <h5 class="mb-0">To: {{ dateEnd }}</h5>
          </div>
          <button
              class="btn btn-primary px-4"
              id="mdl-btn-load"
              type="button"
              data-bs-toggle="modal"
              data-bs-target="#mdl-load"
          >
            <i class="bi bi-upload me-2"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageHeader',
  props: {
    reportType: {
      type: String,
      required: true
    },
    chartName: {
      type: String,
      required: true
    },
    dateStart: {
      type: String,
      required: true
    },
    dateEnd: {
      type: String,
      required: true
    }
  }
}
</script>