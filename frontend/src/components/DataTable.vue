<!-- DataTable.vue -->
<template>
  <div class="container-fluid">
    <h3>Data Table: {{ totalItems }} rows</h3>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Table Container -->
    <div v-else class="table-responsive">
      <table class="table table-striped table-sm">
        <thead>
          <tr>
            <th v-for="header in headers"
                :key="header"
                class="text-xs px-2 py-1">
              {{ prettyHeader(header) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tableData" :key="item.scan_id">
            <td v-for="header in headers"
                :key="header"
                class="text-xs px-2 py-1"
                :title="item[header] && String(item[header]).length > 25 ? item[header] : null">
              {{ formatCellContent(item[header]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 0" aria-label="Table navigation" class="mt-3">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage - 1)">Previous</a>
        </li>
        <li v-for="page in totalPages"
            :key="page"
            class="page-item"
            :class="{ active: page === currentPage }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(page)">{{ page }}</a>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage + 1)">Next</a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const headers = ref([
  'tag_name',
  'hit_type',
  'named_threat',
  'scan_id',
  'incident',
  'provider_name',
  'publisher_name'
])

const currentPage = ref(1)
const itemsPerPage = ref(20)
const totalPages = ref(0)
const totalItems = ref(0)
const tableData = ref([])
const loading = ref(true)

const formatCellContent = (content) => {
  if (!content) return '';
  const stringContent = String(content);
  if (stringContent.length > 25) {
    return stringContent.slice(0, 22) + '...';
  }
  return stringContent;
}

const prettyHeader = (header) => {
  return header
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const fetchData = async (page) => {
  loading.value = true
  try {
    const response = await fetch(
      `http://localhost:5001/table-data?page=${page}&items_per_page=${itemsPerPage.value}`
    )
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    const data = await response.json()

    // Update component state with API response
    tableData.value = data.data
    totalItems.value = data.total
    totalPages.value = data.total_pages
    currentPage.value = data.page
  } catch (error) {
    console.error('Error fetching table data:', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    fetchData(newPage)
  }
}

// Watch for page changes
watch(currentPage, (newPage) => {
  fetchData(newPage)
})

// Initial data fetch
onMounted(() => {
  fetchData(1)
})
</script>

<style scoped>
.pagination {
  margin-bottom: 1rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.text-xs {
  font-size: 0.65rem;
  line-height: 1;
}

.table-sm > :not(caption) > * > * {
  padding: 0.15rem 0.25rem;
}

/* Make table more compact overall */
.table {
  margin-bottom: 0.5rem;
  line-height: 1;
}

/* Ensure header text is aligned with content */
th.text-xs {
  font-weight: 600;
  vertical-align: middle;
}
</style>