Real-Time Quant Analytics Dashboard

Project Overview-->
This project is a real-time quantitative analytics system that ingests live cryptocurrency futures data from Binance Futures WebSocket, processes it in real time, computes key statistical and quantitative metrics, and visualizes them using an interactive dashboard built with Streamlit.

The system focuses on pairs trading analytics such as spread analysis, hedge ratio estimation, rolling correlation, z-score monitoring, and stationarity testing.

Architecture Overview-->
Binance Futures WebSocket
↓
Ingestion Layer (Python WebSocket)
↓
Thread-safe In-Memory Storage
↓
Analytics Engine (Quant Metrics)
↓
Streamlit Dashboard (Frontend)

Technology Stack-->
Programming Language: Python
Data Source: Binance Futures WebSocket (Public)
Ingestion: websocket-client, threading
Storage: In-memory (thread-safe)
Analytics: NumPy, Statsmodels
Frontend: Streamlit
Export: CSV

Data Source-->
Source: Binance Futures public WebSocket
Endpoint:
wss://fstream.binance.com/ws/<symbol>@trade
Symbols: BTCUSDT, ETHUSDT (configurable)
Authentication: Not required (public data)
Type: Real-time trade-level tick data

No preloaded datasets or CSV files are used.

Project Structure-->
quant_analytics_app/
app.py (Streamlit frontend)
ingestion.py (WebSocket ingestion layer)
storage.py (Thread-safe in-memory storage)
analytics.py (Quantitative analytics)
requirements.txt
README.txt

Live Update Strategy-->
Tick-level data is continuously ingested via WebSocket connections.
Data is stored in a thread-safe in-memory buffer.
The Streamlit UI reads from this buffer on every interaction.
Aggregation is performed dynamically based on the selected timeframe.
No blocking loops or timers are used in the UI layer.

This design ensures low latency, stable UI behavior, and clear separation between ingestion and visualization logic.

Features and Analytics-->
Real-Time Ingestion-->
Live Binance Futures trade data
Multi-symbol support
Background threaded WebSocket connections

Data Aggregation-->
Resampling at 1s, 1m, and 5m intervals
Last price and traded volume per interval

Quantitative Analytics-->
Z-score (rolling) to detect deviations
BTC–ETH spread for pairs trading
Rolling correlation between assets
OLS hedge ratio-->
   Current hedge ratio displayed as a numeric metric
   Rolling hedge ratio visualized over time

ADF stationarity test-->
On-demand execution
Displays p-value and interpretation

Alerts-->
Z-score threshold alerts for extreme movements

Visualization-->
Live price charts per symbol
Analytics charts for spread, correlation, hedge ratio
Interactive Streamlit dashboard

Data Export
Download resampled data as CSV -->
Supports offline analysis and backtesting

Performance Considerations-->
In-memory storage is capped to avoid unbounded growth.
Heavy analytics such as rolling OLS regressions are window-limited.
Higher timeframes (1m and 5m) require sufficient data accumulation.
The UI displays warnings when insufficient data is available.

How to Run the Project-->
Step 1: Create and activate virtual environment
python -m venv venv
venv\Scripts\activate (Windows)
Step 2: Install dependencies
pip install -r requirements.txt
Step 3: Run the application
streamlit run app.py

Usage Instructions-->
Enter symbols (comma-separated), for example: btcusdt,ethusdt
Click Start Ingestion
Select resampling timeframe (1s, 1m, or 5m)
Navigate through tabs: Prices, Analytics, Export
Click Run ADF Test to evaluate stationarity
Download processed data as CSV if needed

Notes and Assumptions-->
The system does not persist data to disk by default.
All data exists only during application runtime.
The application is designed for real-time analytics, not historical backtesting.
The architecture can be extended to use databases such as SQLite or time-series databases.

Possible Extensions-->
Persistent storage using SQLite or a time-series database
Multi-pair analytics
Mean-reversion backtesting engine
Order book data ingestion
Advanced alerting mechanisms

Key Takeaway-->
This project demonstrates real-time data ingestion, quantitative financial analytics, clean backend–frontend separation, and a scalable, interview-ready system design.