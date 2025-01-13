<!-- DataTable.vue -->
<template>
  <div class="container-fluid">
    <h3>Data Table: "Total Rows" rows.</h3>
    <!-- Table Container -->
    <div class="table-responsive text-nowrap text-truncate fs-6">
      <table class="table table-striped">
        <thead>
          <tr>
            <th v-for="header in headers" :key="header">{{ prettyHeader(header) }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paginatedData" :key="item.scan_id">
            <td>{{ item.tag_name }}</td>
            <td>{{ item.hit_type }}</td>
            <td>{{ item.named_threat }}</td>
            <td>{{ item.scan_id }}</td>
            <td>{{ item.incident }}</td>
            <td>{{ item.provider_name }}</td>
            <td>{{ item.publisher_name }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <nav aria-label="Table navigation" class="mt-3">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a class="page-link" href="#" @click.prevent="currentPage--">Previous</a>
        </li>
        <li v-for="page in totalPages"
            :key="page"
            class="page-item"
            :class="{ active: page === currentPage }">
          <a class="page-link" href="#" @click.prevent="currentPage = page">{{ page }}</a>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a class="page-link" href="#" @click.prevent="currentPage++">Next</a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

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
const items = ref([])

const totalPages = computed(() => Math.ceil(items.value.length / itemsPerPage.value))
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return items.value.slice(start, end)
})

const prettyHeader = (header) => {
  return header
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const fetchData = async () => {
  try {
    // Example: const response = await fetch('/api/your-endpoint')
    // items.value = await response.json()
    items.value = [] // Replace with your actual data
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.pagination {
  margin-bottom: 1rem;
}
</style>