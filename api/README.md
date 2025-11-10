# Trader Analysis API

RESTful API for accessing hybrid trader analysis and copy-trading recommendations.

## Features

- 🎯 Top trader rankings
- 📊 Persona-based analysis
- 🔍 Advanced trader search and filtering
- 💎 High-confidence recommendations
- ⚠️ Risk-categorized traders
- 📈 Comprehensive statistics

## Quick Start

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Run Analysis (if not already done)

```bash
cd examples
python run_hybrid_analysis.py --data ../data/traders_202510140811.csv --output ../outputs
```

### 3. Start the API Server

```bash
cd api
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & Info

- `GET /` - API information and available endpoints
- `GET /health` - Health check and data availability status

### Analysis Summary

- `GET /api/summary` - Overall analysis summary with key statistics

### Trader Endpoints

- `GET /api/traders/top` - Get top traders by copy-trading score
  - Query params: `limit` (default: 50), `min_score`
  
- `GET /api/traders/{address}` - Get specific trader by wallet address
  
- `GET /api/traders/search` - Advanced trader search with filters
  - Query params: `persona`, `min_score`, `min_trades`, `min_win_rate`, `validated_only`, `limit`
  
- `GET /api/traders/high-confidence` - High-confidence recommendations
  - Query params: `min_score` (default: 0.6), `min_trades` (default: 20)

### Persona Endpoints

- `GET /api/personas` - List all personas with statistics
  
- `GET /api/personas/{persona_name}/top` - Top traders for specific persona
  - Query params: `limit` (default: 10)

### Risk Category Endpoints

- `GET /api/traders/by-risk/{category}` - Traders by risk level
  - Categories: `low`, `medium`, `medium-high`, `high`
  - Query params: `limit` (default: 10)

### Statistics

- `GET /api/stats/overview` - Comprehensive overview statistics
  
- `GET /api/stats/personas` - Detailed persona statistics

### Export

- `GET /api/exports/all-traders` - Export all trader data (large response)

## Usage Examples

### Get Top 10 Traders

```bash
curl http://localhost:8000/api/traders/top?limit=10
```

### Search for Elite Snipers with High Win Rate

```bash
curl "http://localhost:8000/api/traders/search?persona=Elite%20Sniper&min_win_rate=70&validated_only=true"
```

### Get High-Confidence Recommendations

```bash
curl http://localhost:8000/api/traders/high-confidence
```

### Get Low-Risk Traders

```bash
curl http://localhost:8000/api/traders/by-risk/low?limit=20
```

### Get Specific Trader Details

```bash
curl http://localhost:8000/api/traders/12ezPHMdedFwM94YefhRJ9RLhZcsDmX3gJsMKCWt6K9e
```

### Get All Personas

```bash
curl http://localhost:8000/api/personas
```

### Get Analysis Summary

```bash
curl http://localhost:8000/api/summary
```

## Response Format

All endpoints return JSON responses. Example:

```json
{
  "count": 10,
  "traders": [
    {
      "address": "12ezPHMdedFwM94YefhRJ9RLhZcsDmX3gJsMKCWt6K9e",
      "persona": "Elite Sniper",
      "copy_trading_score": 0.814,
      "quality_score": 0.892,
      "total_pnl": 15234.56,
      "roi": 234.5,
      "win_rate": 78.5,
      "total_trades": 145,
      "risk_category": "Low Risk",
      "validation_passed": true
    }
  ]
}
```

## Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get top traders
response = requests.get(f"{BASE_URL}/api/traders/top", params={"limit": 20})
top_traders = response.json()

print(f"Found {top_traders['count']} top traders")
for trader in top_traders['traders'][:5]:
    print(f"{trader['address']}: Score {trader['copy_trading_score']:.3f}")

# Search for specific criteria
response = requests.get(f"{BASE_URL}/api/traders/search", params={
    "min_score": 0.7,
    "min_trades": 50,
    "validated_only": True
})
results = response.json()

print(f"\nFound {results['count']} traders matching criteria")
```

## JavaScript/TypeScript Client Example

```javascript
// Fetch top traders
async function getTopTraders(limit = 50) {
  const response = await fetch(`http://localhost:8000/api/traders/top?limit=${limit}`);
  const data = await response.json();
  return data;
}

// Search traders
async function searchTraders(filters) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`http://localhost:8000/api/traders/search?${params}`);
  const data = await response.json();
  return data;
}

// Usage
const topTraders = await getTopTraders(10);
console.log(`Found ${topTraders.count} top traders`);

const eliteTraders = await searchTraders({
  persona: 'Elite Sniper',
  min_score: 0.7,
  validated_only: true
});
```

## Environment Variables

You can customize the API using environment variables:

- `OUTPUTS_DIR` - Path to outputs directory (default: `../outputs`)
- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8000`)

## CORS Configuration

The API is configured to allow all origins by default. For production, modify the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to specific origins
    allow_credentials=True,
    allow_methods=["GET"],  # Restrict to specific methods
    allow_headers=["*"],
)
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

Error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Performance Considerations

- **Caching**: Consider implementing caching for frequently accessed endpoints
- **Pagination**: Large result sets use the `limit` parameter
- **Export endpoint**: The `/api/exports/all-traders` endpoint returns all data and may be slow for large datasets

## Production Deployment

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY ../outputs ./outputs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t trader-analysis-api .
docker run -p 8000:8000 trader-analysis-api
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## License

Same as parent project.

## Support

For issues or questions, please refer to the main project documentation.
