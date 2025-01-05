# Ad Security Analytics Dashboard

An interactive visualization dashboard that displays ad security threats and anomalies using a hierarchical sunburst chart. The application processes JSON data containing information about different types of security incidents, their sources, and characteristics.

## Features

- Interactive sunburst chart visualization using ECharts
- Hierarchical display of security threats by category
- Color-coded segments for different threat types
- Drill-down capability to explore nested data
- Hover tooltips with detailed information
- Responsive design for different screen sizes

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic for data validation

### Frontend
- Vue.js 3
- ECharts 5
- Axios for API calls
- Tailwind CSS for styling

## Project Structure

```
.
├── README.md
├── api/
│   └── api.py                # FastAPI application
├── data/
│   ├── dataset.csv           # Processed dataset
│   ├── raw/
│   │   └── raw_data_7_days.csv  # Raw input data
│   └── sunburst_data.json    # Processed JSON for visualization
├── dataproc/
│   ├── __init__.py
│   ├── palettes.py          # Color scheme definitions
│   ├── proc_raw.py          # Raw data processing
│   └── process.py           # Main data processing logic
├── frontend/
│   ├── README.md
│   ├── babel.config.js
│   ├── jsconfig.json
│   ├── package.json
│   ├── public/
│   │   ├── ico-manifest/    # App icons and manifests
│   │   └── index.html
│   ├── src/
│   │   ├── App.vue
│   │   ├── assets/
│   │   ├── components/
│   │   │   └── SunburstChart.vue
│   │   └── main.js
│   └── vue.config.js
└── requirements.txt
```

## Data Processing

The application includes a robust data processing pipeline:

1. `dataproc/proc_raw.py`: Processes raw CSV data from the `data/raw` directory
2. `dataproc/palettes.py`: Defines color schemes for different threat categories
3. `dataproc/process.py`: Transforms processed data into the hierarchical structure needed for the sunburst visualization

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ad-security-dashboard
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Start the API server:
```bash
python -m uvicorn api.api:app --reload
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

5. Start the frontend development server:
```bash
npm run serve
```

## API Endpoints

### GET /api/data
Returns the processed sunburst chart data

Response format:
```json
{
  "name": "root",
  "value": number,
  "children": [
    {
      "name": string,
      "value": number,
      "itemStyle": {
        "color": string
      },
      "children": [...]
    }
  ]
}
```

## Frontend Components

### SunburstChart.vue

The main visualization component uses ECharts to render the sunburst diagram:

```vue
<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'SunburstChart',
  // ... component implementation
}
</script>
```

## Data Categories

The visualization includes the following main threat categories:
- Suspicious Activities (Multiple indicators matching known incidents)
- Phishing
- Impression Fraud
- Out-of-browser Redirect
- Compromised Content
- Fake Anti-virus
- Software Install Prompt
- Technical Support Scams

Each category is color-coded and can be drilled down to show:
- DSP sources
- Ad platforms
- Specific threat types
- Incident counts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ECharts for providing the visualization library
- Vue.js team for the reactive framework
- FastAPI team for the efficient backend framework