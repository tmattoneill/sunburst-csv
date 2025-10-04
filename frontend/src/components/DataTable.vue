<!-- DataTable.vue -->
<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="m-0">Data Table: {{ totalItems }} rows</h3>
      <button
        class="btn btn-outline-secondary"
        @click="downloadCurrentView"
        :disabled="loading"
        title="Download current view">
        <i class="bi bi-download"></i>
      </button>
    </div>

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
        <!-- First/Previous -->
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(1)">&lt;&lt;</a>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage - 1)">&lt;</a>
        </li>

        <!-- Page Numbers -->
        <template v-for="page in displayedPages" :key="page">
          <li v-if="page === '...'" class="page-item disabled">
            <span class="page-link">...</span>
          </li>
          <li v-else
              class="page-item"
              :class="{ active: page === currentPage }">
            <a class="page-link" href="#" @click.prevent="handlePageChange(page)">{{ page }}</a>
          </li>
        </template>

        <!-- Next/Last -->
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage + 1)">&gt;</a>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a class="page-link" href="#" @click.prevent="handlePageChange(totalPages)">&gt;&gt;</a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { fetchApi, API_ENDPOINTS } from '@/services/api'

const headers = ref([])  // Will be populated dynamically from data

const currentPage = ref(1)
const itemsPerPage = ref(20)
const totalPages = ref(0)
const totalItems = ref(0)
const tableData = ref([])
const loading = ref(true)

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  },
  rootName: {
    type: String,
    required: true
  },
  dateStart: {
    type: String,
    required: false,
    default: ''
  },
  dateEnd: {
    type: String,
    required: false,
    default: ''
  },
  currentNodeName: {
    type: String,
    required: true
  },
  treeOrder: {
    type: Array,
    required: false,
    default: () => []
  },
  valueColumn: {
    type: String,
    required: false,
    default: ''
  }
})

const formatCellContent = (content) => {
  if (!content) return '';
  const stringContent = String(content);
  return stringContent.length > 25 ? stringContent.slice(0, 22) + '...' : stringContent;
}

const prettyHeader = (header) => {
  return header
    .trim()
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Reorder headers: hierarchy columns, then value column, then others
const reorderHeaders = (allHeaders) => {
  if (!props.treeOrder || props.treeOrder.length === 0) {
    // No tree order defined (legacy mode), return as-is
    return allHeaders
  }

  const ordered = []
  const remaining = [...allHeaders]

  // 1. Add hierarchy columns in tree order
  props.treeOrder.forEach(col => {
    // Trim the column name to match CSV headers (which may have whitespace)
    const trimmedCol = col.trim()
    const found = remaining.find(h => h.trim() === trimmedCol)
    if (found) {
      ordered.push(found)
      remaining.splice(remaining.indexOf(found), 1)
    }
  })

  // 2. Add value column (if not already in hierarchy)
  if (props.valueColumn) {
    const trimmedValueCol = props.valueColumn.trim()
    const found = remaining.find(h => h.trim() === trimmedValueCol)
    if (found) {
      ordered.push(found)
      remaining.splice(remaining.indexOf(found), 1)
    }
  }

  // 3. Add all remaining columns in original CSV order
  ordered.push(...remaining)

  console.log('DataTable - Reordered headers:', {
    original: allHeaders,
    treeOrder: props.treeOrder,
    valueColumn: props.valueColumn,
    reordered: ordered
  })

  return ordered
}

const fetchData = async (page) => {
  loading.value = true;
  try {
    const requestParams = {
      page: page.toString(),
      items_per_page: itemsPerPage.value.toString()
    };

    // Only add filters if they exist and aren't empty
    if (props.filters && Object.keys(props.filters).length > 0) {
      // Log the filters we're about to send
      console.log('DataTable - Current filters:', {
        raw: props.filters,
        stringified: JSON.stringify(props.filters)
      });
      requestParams.filters = props.filters;
    }

    console.log('DataTable - Making API request with params:', requestParams);

    const response = await fetchApi(API_ENDPOINTS.TABLE_DATA, {
      params: requestParams
    });

    // Log the entire response for debugging
    console.log('DataTable - Raw API response:', response);

    // Validate response structure
    if (!response || typeof response !== 'object') {
      throw new Error('Invalid response format: expected object');
    }

    if (!Array.isArray(response.data)) {
      throw new Error('Invalid response data: expected array');
    }

    // Update state with response data
    tableData.value = response.data;
    totalItems.value = Number(response.total) || 0;
    totalPages.value = Number(response.total_pages) || 1;
    currentPage.value = Number(response.page) || 1;

    // Extract headers dynamically from first row of data
    if (response.data.length > 0) {
      const extractedHeaders = Object.keys(response.data[0]);
      const reordered = reorderHeaders(extractedHeaders);
      // Only update if headers have changed (to avoid unnecessary reactivity)
      if (JSON.stringify(headers.value) !== JSON.stringify(reordered)) {
        headers.value = reordered;
        console.log('DataTable - Headers updated from data:', headers.value);
      }
    }

    // Log state updates
    console.log('DataTable - State updated:', {
      rowCount: tableData.value.length,
      totalItems: totalItems.value,
      totalPages: totalPages.value,
      currentPage: currentPage.value,
      headers: headers.value,
      actualData: response.data.slice(0, 2) // Log first two rows as sample
    });

  } catch (error) {
    console.error('DataTable - Error details:', {
      message: error.message,
      filters: props.filters,
      page: page
    });

    // Reset to safe defaults
    tableData.value = [];
    headers.value = [];
    totalItems.value = 0;
    totalPages.value = 1;
    currentPage.value = 1;
  } finally {
    loading.value = false;
  }
};

const downloadCurrentView = async () => {
  try {
    const response = await fetchApi(API_ENDPOINTS.TABLE_DATA, {
      method: 'POST',
      data: props.filters
    })

    const csvRows = [headers.value.join(',')]

    response.data.forEach(item => {
      const values = headers.value.map(header => {
        const value = item[header] ?? ''
        return `"${String(value).replace(/"/g, '""')}"`
      })
      csvRows.push(values.join(','))
    })

    const csvContent = csvRows.join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const filename = `${props.rootName}_${props.dateStart}_${props.dateEnd}_${props.currentNodeName}.csv`
      .replace(/[^a-zA-Z0-9-_]/g, '_')

    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error('Error downloading data:', error)
  }
}

const getDisplayedPages = (current, total) => {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  let pages = []
  pages.push(1)

  if (current <= 4) {
    pages.push(2, 3, 4, 5, '...', total)
  } else if (current >= total - 3) {
    pages.push('...', total - 4, total - 3, total - 2, total - 1, total)
  } else {
    pages.push('...', current - 1, current, current + 1, '...', total)
  }

  return pages
}

const displayedPages = computed(() => getDisplayedPages(currentPage.value, totalPages.value))

const handlePageChange = async (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value && newPage !== currentPage.value) {
    await fetchData(newPage)
  }
}

// Watch for filter changes
watch(
  () => props.filters,
  (newFilters) => {
    console.log('DataTable - Filter watcher triggered with filters:', newFilters)
    currentPage.value = 1
    fetchData(1)
  },
  { deep: true, immediate: true }
)

// Initial data fetch
onMounted(() => {
  console.log('DataTable - Initial mount, filters:', props.filters)
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

.table {
  margin-bottom: 0.5rem;
  line-height: 1;
}

th.text-xs {
  font-weight: 600;
  vertical-align: middle;
}
</style>