# Trader Analysis API - Database Edition

Real-time trader analysis and copy-trading recommendations powered by MySQL database.

## Features

- 🔄 **Real-time Database Integration** - Direct connection to MySQL for live trader data
- 🧠 **Hybrid Analysis** - Combines unsupervised clustering with domain expert rules
- 📊 **Multiple Endpoints** - Comprehensive REST API for all analysis needs
- 🎯 **Smart Recommendations** - AI-powered copy-trading suggestions
- 🔍 **Advanced Filtering** - Query traders by multiple criteria
- 📈 **Persona Classification** - Automatic trader persona discovery and classification
- 🔐 **Secure Configuration** - Environment-based credentials management

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and configure your database credentials:

```bash
cd api
cp .env.example .env
# Edit .env with your database credentials
```

See [CONFIG.md](CONFIG.md) for detailed configuration guide.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API Server

```bash
# Using uvicorn directly
uvicorn main_db:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main_db.py
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## Database Configuration

The API connects to a MySQL database using credentials from environment variables.

**Configuration File:** `.env`

```bash
DB_HOST=your-database-host
DB_PORT=10454
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=solana_tokens
DB_SSL_MODE=DISABLED
```

**⚠️ Security Note:** Never commit your `.env` file to version control!

The database schema includes:
- `wallet_address` - Trader's wallet address
- `token_address` - Token being traded
- `gross_profit` - Total profit including unrealized
- `realized_profit` - Realized profit only
- `realized_profit_percent` - ROI percentage
- `win_rate` - Win rate percentage
- `trades` - Total number of trades
- `trade_volume` - Total trading volume
- `is_bot` - Bot detection flag
- And more...

## API Endpoints

### Core Endpoints

#### 1. Health Check
```bash
GET /
```
Check API and database connection status.

#### 2. Database Statistics
```bash
GET /api/v1/stats
```
Get overall database statistics including totals and averages.

**Example Response:**
```json
{
  "total_traders": 15000,
  "non_bot_traders": 12000,
  "bot_traders": 3000,
  "avg_win_rate": 45.5,
  "avg_trades": 120,
  "avg_volume": 50000,
  "avg_profit": 1500,
  "total_profit": 18000000,
  "analysis_available": true
}
```

### Trader Query Endpoints

#### 3. Get All Traders
```bash
GET /api/v1/traders?exclude_bots=true&limit=100&offset=0
```

Query parameters:
- `exclude_bots` (bool): Exclude bot accounts (default: true)
- `limit` (int): Maximum results (1-1000, default: 100)
- `offset` (int): Pagination offset (default: 0)

#### 4. Get Trader by Address
```bash
GET /api/v1/traders/{wallet_address}
```

Get detailed information for a specific trader.

**Example:**
```bash
curl http://localhost:8000/api/v1/traders/ABC123...XYZ
```

#### 5. Get Top Traders
```bash
GET /api/v1/traders/top/ranked?limit=50&sort_by=realized_profit&exclude_bots=true
```

Query parameters:
- `limit` (int): Number of top traders (1-500, default: 50)
- `sort_by` (str): Sort metric (default: "realized_profit")
  - Options: `realized_profit`, `gross_profit`, `win_rate`, `trade_volume`, `trades`
- `exclude_bots` (bool): Exclude bots (default: true)

#### 6. Filter Traders
```bash
GET /api/v1/traders/filter?min_win_rate=60&min_trades=100&min_profit=1000
```

Query parameters:
- `min_win_rate` (float): Minimum win rate % (0-100)
- `min_trades` (int): Minimum number of trades
- `min_volume` (float): Minimum trade volume
- `min_profit` (float): Minimum realized profit
- `exclude_bots` (bool): Exclude bots (default: true)
- `limit` (int): Maximum results (default: 100)

### Analysis Endpoints

#### 7. Run Hybrid Analysis
```bash
POST /api/v1/analysis/run
```

Trigger a new hybrid analysis run on all traders. This:
- Fetches latest data from database
- Filters out bots
- Prepares features
- Runs hybrid persona classification
- Calculates quality scores and copy-trading scores
- Caches results

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/analysis/run
```

**Response:**
```json
{
  "status": "success",
  "message": "Analysis completed for 12000 traders",
  "timestamp": "2025-11-10T15:30:00",
  "traders_analyzed": 12000
}
```

#### 8. Get Analysis Results
```bash
GET /api/v1/analysis/results?limit=100&persona=Elite+Sniper&min_copy_trading_score=80
```

Query parameters:
- `limit` (int): Maximum results (1-1000, default: 100)
- `offset` (int): Pagination offset (default: 0)
- `persona` (str): Filter by persona type (optional)
- `min_copy_trading_score` (float): Minimum score (0-100, optional)

**Example Response:**
```json
{
  "total_results": 12000,
  "filtered_results": 150,
  "results": [
    {
      "address": "ABC123...XYZ",
      "persona": "Elite Sniper",
      "copy_trading_score": 92.5,
      "quality_score": 88.3,
      "realized_profit": 25000,
      "win_rate": 75.5,
      "risk_category": "medium"
    }
  ],
  "analysis_timestamp": "2025-11-10T15:30:00"
}
```

#### 9. Get Persona Statistics
```bash
GET /api/v1/analysis/personas
```

Get statistics for each discovered trading persona.

**Example Response:**
```json
{
  "total_personas": 6,
  "total_classified_traders": 11500,
  "personas": [
    {
      "persona": "Elite Sniper",
      "trader_count": 2500,
      "avg_copy_trading_score": 85.5,
      "avg_quality_score": 82.1,
      "avg_realized_profit": 15000,
      "avg_win_rate": 68.5,
      "total_volume": 125000000
    }
  ]
}
```

#### 10. Get Copy Trading Recommendations
```bash
GET /api/v1/analysis/recommendations?min_score=70&limit=50
```

Get top copy-trading recommendations with quality validation.

Query parameters:
- `min_score` (float): Minimum copy trading score (0-100, default: 70)
- `limit` (int): Maximum recommendations (1-500, default: 50)

**Example Response:**
```json
{
  "total_recommendations": 45,
  "min_score_threshold": 70,
  "recommendations": [
    {
      "address": "ABC123...XYZ",
      "persona": "Elite Sniper",
      "copy_trading_score": 92.5,
      "quality_score": 88.3,
      "realized_pnl": 25000,
      "roi": 150.5,
      "win_rate": 75.5,
      "total_trades": 250,
      "total_volume": 500000,
      "risk_category": "medium",
      "profit_factor": 3.5
    }
  ]
}
```

## Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Check health
response = requests.get(f"{BASE_URL}/")
print(response.json())

# Run analysis
response = requests.post(f"{BASE_URL}/api/v1/analysis/run")
print(response.json())

# Get recommendations
response = requests.get(
    f"{BASE_URL}/api/v1/analysis/recommendations",
    params={"min_score": 80, "limit": 20}
)
recommendations = response.json()
print(f"Found {len(recommendations['recommendations'])} recommendations")

# Filter traders
response = requests.get(
    f"{BASE_URL}/api/v1/traders/filter",
    params={
        "min_win_rate": 60,
        "min_trades": 100,
        "min_profit": 5000,
        "limit": 50
    }
)
traders = response.json()
print(f"Found {len(traders)} traders matching criteria")
```

### JavaScript/Node.js Client

```javascript
const BASE_URL = "http://localhost:8000";

// Run analysis
async function runAnalysis() {
  const response = await fetch(`${BASE_URL}/api/v1/analysis/run`, {
    method: 'POST'
  });
  const data = await response.json();
  console.log(data);
}

// Get recommendations
async function getRecommendations() {
  const response = await fetch(
    `${BASE_URL}/api/v1/analysis/recommendations?min_score=80&limit=20`
  );
  const data = await response.json();
  console.log(`Found ${data.recommendations.length} recommendations`);
  return data.recommendations;
}

// Get persona stats
async function getPersonaStats() {
  const response = await fetch(`${BASE_URL}/api/v1/analysis/personas`);
  const data = await response.json();
  console.log(`Discovered ${data.total_personas} personas`);
  return data.personas;
}
```

### cURL Examples

```bash
# Get database stats
curl http://localhost:8000/api/v1/stats

# Run analysis
curl -X POST http://localhost:8000/api/v1/analysis/run

# Get top traders by profit
curl "http://localhost:8000/api/v1/traders/top/ranked?limit=10&sort_by=realized_profit"

# Get recommendations
curl "http://localhost:8000/api/v1/analysis/recommendations?min_score=80&limit=20"

# Filter high-performance traders
curl "http://localhost:8000/api/v1/traders/filter?min_win_rate=70&min_trades=200&min_profit=10000"

# Get specific trader
curl http://localhost:8000/api/v1/traders/YOUR_WALLET_ADDRESS

# Get persona statistics
curl http://localhost:8000/api/v1/analysis/personas
```

## Analysis Workflow

1. **Initial Setup**: API connects to database on startup
2. **Data Retrieval**: Fetch trader data from MySQL database
3. **Feature Engineering**: Calculate derived metrics (profit factor, ROI, etc.)
4. **Hybrid Classification**: 
   - Unsupervised clustering to discover patterns
   - Domain rules for known personas
   - Confidence scoring for classifications
5. **Quality Scoring**: Multi-factor quality assessment
6. **Copy Trading Scoring**: Calculate suitability scores for copy trading
7. **Caching**: Results cached for fast retrieval
8. **API Access**: Results available through REST endpoints

## Performance Considerations

- **Caching**: Analysis results are cached to avoid repeated computation
- **Connection Pooling**: Database connections are pooled for efficiency
- **Pagination**: Large result sets support offset/limit pagination
- **Background Tasks**: Long-running analysis can be backgrounded
- **SSL**: Database SSL verification disabled for compatibility

## Troubleshooting

### Database Connection Issues

If you see SSL errors:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

The API is configured to disable SSL verification. Check `db_service.py` configuration.

### Analysis Not Running

If analysis endpoint returns errors:
- Ensure database has sufficient traders (minimum 10)
- Check that traders table has all required columns
- Verify bots are being filtered correctly

### Missing Dependencies

Install all required packages:
```bash
pip install -r requirements.txt
```

## Development

### Project Structure

```
api/
├── main_db.py           # Main FastAPI application with database integration
├── db_service.py        # Database service layer
├── db_explorer.py       # Database schema explorer
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Endpoints

1. Define Pydantic models for request/response
2. Add endpoint function with proper decorators
3. Implement business logic using db_service
4. Add error handling and logging
5. Update this README

## License

This project is part of the trader-selection analysis system.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review logs for error messages
3. Verify database connection and schema
4. Test with the provided examples

## Next Steps

- [ ] Add WebSocket support for real-time updates
- [ ] Implement authentication/API keys
- [ ] Add rate limiting
- [ ] Export analysis to various formats (PDF, Excel)
- [ ] Add more advanced filtering options
- [ ] Implement trader comparison endpoints
