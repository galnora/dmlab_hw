
# Big Pharma Stock Analytics 

This project implements a microservice-based data pipeline that collects stock market time-series data from the public AlphaVantage API, processes and stores it in a MySQL database, computes business-relevant analytics, and exposes the results through a REST API and a visual dashboard.
The focus of the exercise is demonstrating real-world backend architecture: data ingestion, processing, API design, containerization, scheduling, and visualization.


## Architecture

```
+----------------+         +----------------+         +----------------+
|    Collector   | ----->  |    Processor   | ----->  |    Dashboard   |
+----------------+         +----------------+         +----------------+
         |                         |
         v                         v
   AlphaVantage API            MySQL Database
```

### Collector
Fetches daily or full historical stock data and sends it to the processor for ingestion.
### Processor
Stores data in MySQL, computes derived metrics (growth, volatility, MoM change, etc.), and exposes multiple REST API endpoints.
### Dashboard
FastAPI + Jinja2 + Chart.js app that visualizes trends and analytics.
### Scheduler
Runs the daily collector via cron inside a dedicated container.
## Tech Stack

### Backend
Python 3.11

FastAPI (REST API & backend services)

MySQL 8 (relational data storage)

Pandas, NumPy (data processing & analytics)
### Frontend
Chart.js + Annotation Plugin (interactive visualizations)

Jinja2 templates

Vanilla JS & HTML/CSS
### Infrastructure
Docker & Docker Compose

Cron-based Scheduler (daily ingestion)

Multi-service containerized architecture
### External Services
AlphaVantage Public API (stock market data source)



## Environment Variables

The project uses .env for configuration. A sample file is provided.
### Create your environment file:
```cp .env.example .env```

### Fill in your AlphaVantage API key:
``` ALPHAVANTAGE_API_KEY=YOUR_KEY_HERE ```


## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```
Create .env

```bash
  cp .env.sample .env
```
Fill in your API key.

Build and start the services

```bash
  docker-compose up --build -d
```

Access the dashboard on http://localhost:8000

Check the logs

```bash
  docker-compose logs -f
```


## API Reference

#### Ingest stock records

```http
  POST /api/v1/ingest/{symbol}
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `symbol` | `string` | **Required**. Stock ticker symbol |

#### Body:
List of stock records with: `date`, `open`, `high`, `low`, `close`, `volume`

#### Get full trend data

```http
  GET /api/v1/trend/{symbol}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `symbol`      | `string` | **Required**. Stock ticker symbol |

#### Returns:
Full time-series data (close price, volume, date) from 2017 onward.

#### Get period-based growth metrics

```http
  GET /api/v1/metrics/{symbol}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `symbol`      | `string` | **Required**. Stock ticker symbol |

#### Returns:
Pre-COVID growth (%)
COVID-period growth (%)
Post-COVID growth (%)

#### Get analytics (volatility, MoM change, volume)

```http
  GET /api/v1/analytics/{symbol}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `symbol`      | `string` | **Required**. Stock ticker symbol |

#### Returns:
Annualized volatility
Month-over-month percent change
Average trading volume



## Services
### Collector Service
Fetches full or daily data from AlphaVantage (`TIME_SERIES_DAILY`)
Converts records into normalized JSON
Sends them to Processor’s ingest endpoint
### Processor Service
Provides structured API access to stored stock data
Computes business-valuable metrics
Manages ingestion and DB writes
### Dashboard Service
Visualizes the time series with COVID-phase annotations
Displays growth percentages, volatility, MoM change, and volume
### Scheduler Service
Runs the daily collector via cron
Ensures fresh daily updates