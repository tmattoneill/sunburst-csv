# Sunburst Chart Visualization

A Vue-based application for visualizing hierarchical data as interactive sunburst charts, supported by a Flask backend for serving data.

## Features

- Interactive Sunburst Charts - Visualize complex hierarchical data in a clear and engaging way
- Responsive Design - Works seamlessly across devices
- Backend Integration - A Flask API serves dynamic JSON data for the charts
- Customizable Styling - Designed with user-friendly and visually appealing themes

## Project Structure
```
.
├── README.md
├── api
│   └── api.py
├── data
│   ├── dataset.csv
│   ├── raw
│   │   └── raw_data_7_days.csv
│   └── sunburst_data.json
├── dataproc
│   ├── __init__.py
│   └── report_processor.py
├── frontend
│   ├── babel.config.js
│   ├── jsconfig.json
│   ├── package.json
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── App.vue
│   │   ├── assets
│   │   │   └── logo.png
│   │   ├── components
│   │   │   └── SunburstChart.vue
│   │   ├── main.js
│   │   └── palettes.js
│   └── vue.config.js
└── requirements.txt
```

## Requirements

### Frontend
- Vue.js v3.5.13
- ECharts v5.6.0

### Backend
- Python >= 3.8
- Flask 3.0.2
- Flask-CORS 4.0.0
- Pandas 2.2.3
- Requests 2.3.0

## Setup

### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run serve
```

### Backend Setup
```bash
# Install Python requirements
pip install -r requirements.txt

# Start Flask server
python api.py
```

The backend will run on http://localhost:5001

## Data Format

The sunburst chart expects hierarchical JSON data stored in `sunburst_data.json`. Example structure:

```json
{
  "name": "Root",
  "value": 100,
  "children": [
    {
      "name": "Branch 1",
      "value": 60,
      "children": [
        { "name": "Leaf 1", "value": 30 },
        { "name": "Leaf 2", "value": 30 }
      ]
    },
    {
      "name": "Branch 2",
      "value": 40
    }
  ]
}
```

## Available Scripts

### Frontend
```bash
npm run serve   # Start development server
npm run build   # Build for production
npm run lint    # Lint and fix files
```

### Backend
```bash
python api.py   # Start Flask server
```

## Contributing

1. Fork this repository
2. Create a new feature branch
3. Commit your changes
4. Open a pull request

## License

This project is licensed under the ISC License. See `LICENSE` for more information.