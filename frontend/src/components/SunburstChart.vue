<script setup>
import { ref, watch, onMounted, onBeforeUnmount, defineProps, defineEmits } from 'vue'
import * as echarts from 'echarts'
import { PALETTES } from '@/palettes'


// Props
const props = defineProps({
  chartData: {
    type: Object,
    required: true,
  },
  paletteName: {
    type: String,
    default: 'ocean'
  }
})

// Emits
const emit = defineEmits(['update:paletteName', 'node-click', 'node-hover'])

// Refs
const chart = ref(null)
const currentData = ref(null)
const selectedPalette = ref(props.paletteName)
const chartContainer = ref(null)
const colors = ref(PALETTES[props.paletteName] || PALETTES.Ocean)

watch(() => props.paletteName, (newPalette) => {
  colors.value = PALETTES[newPalette] || PALETTES.Ocean;
  if (chart.value) {
    updateChart();
  }
}, { immediate: true });

// Computed
// const paletteNames = computed(() => Object.keys(PALETTES))
//
// // Methods
// const handlePaletteChange = () => {
//   colors.value = PALETTES[selectedPalette.value]
//   emit('update:paletteName', selectedPalette.value)
//   updateChart()
// }

const handleChartHover = (params) => {
  if (params.data) {
    emit('node-hover', params.data)
  }
}

const handleChartMouseOut = () => {
  emit('node-hover', null); // Emit null when the mouse leaves the chart
};

const getChildrenColors = (data, index) => {
  if (!data || !data.children) {
    return []
  }

  return data.children.map((child, childIndex) => {
    const newIndex = (index + childIndex) % colors.value.length
    return {
      ...child,
      itemStyle: { color: colors.value[newIndex] },
      children: getChildrenColors(child, newIndex)
    }
  })
}

const applyColorsToData = (data) => {
  if (data) {
    return {
      ...data,
      children: getChildrenColors(data, 0)
    }
  }
  return data
}

const handleChartClick = (params) => {
  if (params.data) {
    emit('node-click', params.data)  // Emit the clicked node data
    if (params.data.children) {
      currentData.value = params.data
      renderChart()
    }
  }
}

const renderChart = () => {
  if (!chartContainer.value) return

  chart.value = echarts.init(chartContainer.value)

  const option = {
    series: {
      type: 'sunburst',
      data: [applyColorsToData(currentData.value)],
      radius: ['0%', '100%'],
      center: ['50%', '50%'],
      levels: [{
        // Configure only the center/root level
        r0: '0%',
        r: '15%',
        itemStyle: {
          color: 'none',  // Make the center transparent
          borderWidth: 0  // Remove the border
        },
        label: {
          show: true,
          position: 'center',
          fontSize: 14,
          formatter: (params) => {
            return params.treePathInfo.length === 1 ? params.data.name : ''
          }
        }
      }],
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: false
        }
      }
    },
  }

  chart.value.setOption(option)
  chart.value.on('click', handleChartClick)
  chart.value.on('mouseover', handleChartHover)
  chart.value.on('mouseout', handleChartMouseOut);
}

const updateChart = () => {
  if (chart.value) {
    currentData.value = props.chartData
    renderChart()
  }
}

// Watchers
watch(() => props.chartData, () => {
  updateChart()
}, { deep: true })

watch(() => props.paletteName, (newPalette) => {
  selectedPalette.value = newPalette
  colors.value = PALETTES[newPalette] || PALETTES.Ocean
  if (chart.value) {
    updateChart()
  }
}, { immediate: true })

// Lifecycle hooks
onMounted(() => {
  currentData.value = props.chartData
  renderChart()
})

onBeforeUnmount(() => {
  if (chart.value) {
    chart.value.dispose()
  }
})
</script>

<template>
  <div class="chart-section">
    <!-- Palette Selector Row -->
<!--    <div class="row g-0 mb-2">-->
<!--      <div class="col-12">-->
<!--        <div class="d-flex justify-content-end">-->
<!--          <select v-model="selectedPalette"-->
<!--                  @change="handlePaletteChange"-->
<!--                  class="form-select form-select-sm w-auto">-->
<!--            <option v-for="name in paletteNames" :key="name" :value="name">-->
<!--              {{ name }}-->
<!--            </option>-->
<!--          </select>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

    <!-- Chart Container -->
    <div class="row g-0">
      <div class="col-12">
        <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
      </div>
    </div>
  </div>
</template>



<style scoped>
/* Only keeping minimal required custom styles */
.chart-section {
  width: 100%;
}

.form-select-sm {
  font-size: 0.875rem;  /* 14px */
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
</style>