# ✈ AE Flight Tracker

A real-time flight tracking web application built with Python Flask and Leaflet.js, powered by the OpenSky Network and AviationStack APIs.

![Flight Tracker](https://img.shields.io/badge/Python-3.8-blue?style=flat-square&logo=python) ![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask) ![Leaflet](https://img.shields.io/badge/Leaflet.js-1.9-green?style=flat-square)

---

## Features

- **Live World Map** — Real-time plane positions for 10,000+ flights using Leaflet.js with dark CartoDB tiles
- **Flight Search** — Search any flight or country directly on the map
- **Live Stats** — Total flights, airborne count, average altitude and speed updated in real time
- **Airline Logos** — Airline logo shown when clicking any plane on the map
- **Flight Tracker** — Add any flight by IATA code (e.g. `QR350`, `EK201`) and track its progress
- **Progress Bar** — Animated plane progress bar showing departure → arrival with real times and percentage
- **Auto Refresh** — Data refreshes every 2 minutes automatically

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.8, Flask, Flask-CORS |
| Frontend | HTML, CSS, JavaScript |
| Map | Leaflet.js, CartoDB dark tiles |
| Live Flights | OpenSky Network REST API |
| Flight Info | AviationStack API |
| Data Processing | pandas |

---

## Project Structure

```
flight-tracker/
├── app/
│   ├── app.py              # Flask backend — API routes and data fetching
│   └── templates/
│       └── index.html      # Full frontend — map, stats, flight tracker UI
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/AhmedGElnaggar/Flight-tracker.git
cd Flight-tracker/app

# Install dependencies
pip install flask flask-cors requests pandas
```

### Run

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Serves the main UI |
| `GET /api/flights` | Returns all live flights from OpenSky |
| `GET /api/stats` | Returns aggregated flight statistics |
| `GET /api/track/<flight>` | Validates and tracks a flight via AviationStack |

---

## Data Sources

- **[OpenSky Network](https://opensky-network.org)** — Free real-time ADS-B flight state data
- **[AviationStack](https://aviationstack.com)** — Flight schedules, status, and airport information

---

## Author

**Ahmed Elnaggar** — [GitHub](https://github.com/AhmedGElnaggar)
