<!-- DataTable.vue -->
<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="m-0" v-if="activeTab === 'table'">Data Table: {{ totalItems }} rows</h3>
      <h3 class="m-0" v-else>AI Summary</h3>
      <button
        v-if="activeTab === 'table'"
        class="btn btn-outline-secondary"
        @click="downloadCurrentView"
        :disabled="loading"
        title="Download current view">
        <i class="bi bi-download"></i>
      </button>
    </div>

    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <button
          type="button"
          class="nav-link"
          :class="{ active: activeTab === 'summary' }"
          @click="setActiveTab('summary')"
          :aria-selected="activeTab === 'summary'">
          Summary
        </button>
      </li>
      <li class="nav-item">
        <button
          type="button"
          class="nav-link"
          :class="{ active: activeTab === 'table' }"
          @click="setActiveTab('table')"
          :aria-selected="activeTab === 'table'">
          Table
        </button>
      </li>
    </ul>

    <div v-if="activeTab === 'summary'" class="summary-panel">
      <div v-if="summaryLoading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading summary...</span>
        </div>
      </div>
      <div v-else>
        <p v-if="summaryStatus === 'ready'" class="summary-text mb-3">{{ summaryText }}</p>
        <p v-else-if="summaryStatus === 'pending'" class="text-muted mb-3">
          Generating insights... this usually takes a few seconds.
        </p>
        <p v-else class="text-danger mb-3">{{ summaryText }}</p>
        <p v-if="summaryGeneratedAt" class="text-muted small mb-0">
          Updated {{ formattedSummaryTimestamp }}
        </p>
      </div>
    </div>

    <template v-else>
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading table...</span>
        </div>
      </div>

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

      <nav v-if="totalPages > 0" aria-label="Table navigation" class="mt-3">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="handlePageChange(1)">&lt;&lt;</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage - 1)">&lt;</a>
          </li>

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

          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage + 1)">&gt;</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="handlePageChange(totalPages)">&gt;&gt;</a>
          </li>
        </ul>
      </nav>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { fetchApi, API_ENDPOINTS } from '@/services/api'

const headers = ref([])  // Will be populated dynamically from data

const currentPage = ref(1)
const itemsPerPage = ref(20)
const totalPages = ref(0)
const totalItems = ref(0)
const tableData = ref([])
const loading = ref(true)
const activeTab = ref('table')

const summaryLoading = ref(false)
const summaryStatus = ref('pending')
const summaryText = ref('')
const summaryGeneratedAt = ref('')
let summaryPollHandle = null

const props = defineProps({
  sessionId: {
    type: String,
    required: true
  },
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

  return ordered
}

const fetchData = async (page) => {
  loading.value = true;
  try {
    const requestParams = {
      page: page.toString(),
      items_per_page: itemsPerPage.value.toString(),
      session_id: props.sessionId
    };

    // Only add filters if they exist and aren't empty
    if (props.filters && Object.keys(props.filters).length > 0) {
      requestParams.filters = props.filters;
    }

    const response = await fetchApi(API_ENDPOINTS.TABLE_DATA, {
      params: requestParams
    });

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
      }
    }

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

const clearSummaryPoll = () => {
  if (summaryPollHandle) {
    clearTimeout(summaryPollHandle)
    summaryPollHandle = null
  }
}

const resetSummaryState = () => {
  clearSummaryPoll()
  summaryStatus.value = 'pending'
  summaryText.value = ''
  summaryGeneratedAt.value = ''
  summaryLoading.value = false
}

const fetchSummary = async () => {
  if (!props.sessionId) {
    return
  }

  clearSummaryPoll()
  summaryLoading.value = true

  try {
    const response = await fetchApi(API_ENDPOINTS.TABLE_SUMMARY, {
      params: {
        session_id: props.sessionId
      }
    })

    summaryStatus.value = response.status || 'pending'
    summaryText.value = response.summary || ''
    summaryGeneratedAt.value = response.generated_at || ''

    if (summaryStatus.value === 'pending') {
      summaryPollHandle = setTimeout(fetchSummary, 4000)
    }
  } catch (error) {
    summaryStatus.value = 'error'
    summaryText.value = error.message
    summaryGeneratedAt.value = ''
  } finally {
    summaryLoading.value = false
  }
}

const setActiveTab = (tab) => {
  if (activeTab.value === tab) {
    return
  }

  activeTab.value = tab

  if (tab === 'summary' && summaryStatus.value !== 'ready') {
    fetchSummary()
  }
}

const formattedSummaryTimestamp = computed(() => {
  if (!summaryGeneratedAt.value) {
    return ''
  }

  try {
    return new Date(summaryGeneratedAt.value).toLocaleString()
  } catch (error) {
    console.warn('Failed to format summary timestamp:', error)
    return summaryGeneratedAt.value
  }
})

const downloadCurrentView = async () => {
  try {
    const response = await fetchApi(API_ENDPOINTS.TABLE_DATA, {
      method: 'POST',
      data: {
        ...props.filters,
        session_id: props.sessionId
      }
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
    // Only fetch if sessionId is set
    if (props.sessionId) {
      currentPage.value = 1
      fetchData(1)
    }
  },
  { deep: true }
)

// Refresh when session changes
watch(
  () => props.sessionId,
  (newSession, oldSession) => {
    if (!newSession || newSession === oldSession) {
      return
    }

    currentPage.value = 1
    resetSummaryState()
    fetchSummary()
    fetchData(1)
  }
)

// Initial data fetch
onMounted(() => {
  // Only fetch if sessionId is set
  if (props.sessionId) {
    fetchData(1)
    fetchSummary()
  }
})

onBeforeUnmount(() => {
  clearSummaryPoll()
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

.summary-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1.5rem;
  min-height: 220px;
}

.summary-text {
  white-space: pre-line;
  font-size: 0.95rem;
  line-height: 1.4;
}
</style>
