# Brazilian Stocks Market API

A comprehensive API for accessing 40+ fundamental data points from the Brazilian Stock Market, featuring an API Key system for secure access and optimal performance.

Built for the [Mansa](https://github.com/mansa-team) project and designed for integration with Retrieval-Augmented Generation (RAG) systems.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/heitorrosa/stocks-api
    cd stocks-api
    ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create environment configuration (`.env`):
   ```env
    #
    #$ DATABASE CONFIGURATION
    #
    MYSQL_USER=user
    MYSQL_PASSWORD=password
    MYSQL_HOST=localhost
    MYSQL_DATABASE=database

    #
    #$ STOCKS API
    #
    STOCKSAPI_ENABLED=TRUE
    STOCKSAPI_HOST=localhost
    STOCKSAPI_PORT=3200
    
    STOCKSAPI_KEY.SYSTEM=TRUE
    STOCKSAPI_PRIVATE.KEY=your_api_key_here
   ```

4. Run the server:
    ```bash
    python src/__init__.py
    ```

## API Endpoints

### Health Check
```bash
curl http://localhost:3200/health
```
Returns service status and timestamp.

### API Key Verification
```bash
curl -H "X-API-Key: YOUR_KEY" http://localhost:3200/api/key
```

### Historical Data
Query financial metrics across multiple years:
```bash
curl -H "X-API-Key: YOUR_KEY" "http://localhost:3200/api/historical?search=PETR4&fields=DY,LUCRO%20LIQUIDO&years=2020,2024"
```
**Parameters:**
- `search`: Ticker symbol or company name
- `fields`: Comma-separated field names
- `years`: Single year or range (e.g., `2020` or `2020,2024`)

### Fundamental Data
Query current valuations and metrics by date range:
```bash
curl -H "X-API-Key: YOUR_KEY" "http://localhost:3200/api/fundamental?search=VALE3&fields=ROE,P/L,PRECO&dates=2024-01-01,2024-12-31"
```
**Parameters:**
- `search`: Ticker symbol or company name
- `fields`: Comma-separated field names
- `dates`: Single date or range (supports YYYY, YYYY-MM, or YYYY-MM-DD formats)

## TODO

- [ ] **MySQL-Linked Key System**: Migrate from environment-based API keys to a database-driven key management system with per-user authentication, key rotation, and usage tracking
- [ ] **Rate Limiting**: Implement request rate limiting based on API key tier to prevent abuse and ensure fair resource allocation across clients
- [ ] **Caching Layer**: Add Redis caching for frequently requested data to reduce database load

## License
GNU GENERAL PUBLIC LICENSE MODIFIED v1.0 - Mansa Team. See LICENSE for details.
