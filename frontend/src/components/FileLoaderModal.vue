<template>
  <div class="modal fade" role="dialog" tabindex="-1" id="mdl-load">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">File Loader</h4>
          <button class="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="file" @change="handleFileSelect" accept=".csv">
          <p>Select a valid CSV data source.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-light" type="button" data-bs-dismiss="modal">Close</button>
          <button
              class="btn btn-primary"
              type="button"
              @click="loadFile"
              :disabled="!selectedFile"
              data-bs-dismiss="modal"
          >
            Load
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FileLoaderModal',
  data() {
    return {
      selectedFile: null
    }
  },
  methods: {
    handleFileSelect(event) {
      this.selectedFile = event.target.files[0]
    },
    async loadFile() {
      if (!this.selectedFile) return

      try {
        // Emit the file to parent component
        this.$emit('file-selected', this.selectedFile)

        // Reset selection
        this.selectedFile = null
      } catch (error) {
        console.error('Error loading file:', error)
      }
    }
  }
}
</script>