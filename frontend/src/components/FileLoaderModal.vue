<template>
  <div
    class="modal fade"
    id="mdl-load"
    tabindex="-1"
    aria-labelledby="mdl-load-label"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="mdl-load-label">Upload File</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <input
            type="file"
            @change="handleFileChange"
            class="form-control mb-3"
          />
          <input
            type="text"
            id="mdl-txt-client_name"
            class="form-control"
            placeholder="Enter Client Name"
            v-model="clientName"
          />
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Close
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click="uploadFileAndProcess"
          >
            Upload
          </button>
        </div>
        <div
          class="alert mt-3"
          :class="uploadStatus.includes('successfully') ? 'alert-success' : 'alert-danger'"
          v-if="uploadStatus"
        >
          {{ uploadStatus }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const selectedFile = ref(null);
const clientName = ref("");
const uploadStatus = ref("");

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

const uploadFileAndProcess = async () => {
  if (!selectedFile.value) {
    uploadStatus.value = "No file selected.";
    return;
  }

  if (!clientName.value.trim()) {
    uploadStatus.value = "Client name is required.";
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    const response = await fetch("http://localhost:5001/upload", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();

    if (response.ok) {
      uploadStatus.value = "File uploaded successfully! Running report...";

      // Trigger report processor
      await runReportProcessor(result.filePath, clientName.value);
    } else {
      uploadStatus.value = `Error: ${result.error}`;
    }
  } catch (error) {
    console.error("Upload error:", error);
    uploadStatus.value = "An unexpected error occurred.";
  }
};

const runReportProcessor = async (filePath, clientName) => {
  try {
    const response = await fetch("http://localhost:5001/process", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        filePath,
        clientName,
      }),
    });

    const result = await response.json();

    if (response.ok) {
      uploadStatus.value = "Report processed successfully!";
    } else {
      uploadStatus.value = `Processing error: ${result.error}`;
    }
  } catch (error) {
    console.error("Processing error:", error);
    uploadStatus.value = "An error occurred during report processing.";
  }
};
</script>

<style scoped>
.modal-body {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.alert {
  margin-top: 1rem;
}
</style>
