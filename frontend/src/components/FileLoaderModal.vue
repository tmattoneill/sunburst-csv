<!-- FileLoaderModal.vue: File Loader Modal -->
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
            @keyup.enter="uploadFileAndProcess"
          />
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
            @click="handleClose"
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
import { ref, onMounted } from 'vue';

const selectedFile = ref(null);
const clientName = ref("");
const uploadStatus = ref("");
const emit = defineEmits(['upload-complete']);

const resetForm = () => {
  selectedFile.value = null;
  clientName.value = "";
  uploadStatus.value = "";
  // Reset the file input
  const fileInput = document.querySelector('input[type="file"]');
  if (fileInput) fileInput.value = '';
};

// In FileLoaderModal.vue, update the handleClose function:
const handleClose = () => {
  const modal = bootstrap.Modal.getInstance(document.getElementById('mdl-load'));
  if (modal) {
    modal.hide();
  }
  resetForm();
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
    // Upload file
    const response = await fetch("http://localhost:6500/api/upload", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();

    if (response.ok) {
      uploadStatus.value = "File uploaded successfully! Running report...";

      // Process report
      const processResponse = await fetch("http://localhost:6500/api/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          filePath: result.filePath,
          clientName: clientName.value,
        }),
      });

      if (processResponse.ok) {
        uploadStatus.value = "Report processed successfully!";
        // Don't reset form here - wait for user to close modal

        // Show success message for 3 seconds before allowing close
        await new Promise(resolve => setTimeout(resolve, 3000));
        emit('upload-complete');
      } else {
        uploadStatus.value = "Error processing report.";
      }
    } else {
      uploadStatus.value = `Error: ${result.error}`;
    }
  } catch (error) {
    console.error("Upload error:", error);
    uploadStatus.value = "An unexpected error occurred.";
  }
};

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

// Add mounted hook to handle modal show
onMounted(() => {
  const modal = document.getElementById('mdl-load');
  modal.addEventListener('show.bs.modal', () => {
    modal.style.display = 'block';
    modal.removeAttribute('aria-hidden');
    const firstFocusableElement = modal.querySelector('input[type="file"]');
    if (firstFocusableElement) {
      firstFocusableElement.focus();
    }
  });
});
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
