# YGG Torrent Authentication API

A REST API for remote authentication and cookie generation for YGG Torrent.

## Features

- ✅ **Automated Authentication** - Bypass Cloudflare and authenticate automatically
- ✅ **Cookie Generation** - Generate fresh authentication cookies
- ✅ **Remote Access** - Use from any remote location
- ✅ **Category Browsing** - Get available categories and RSS feeds
- ✅ **Status Checking** - Verify cookie validity
- ✅ **CORS Enabled** - Use from web applications

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements_api.txt
```

2. Start the API server:
```bash
python3 ygg_api.py
```

The API will be available at `http://localhost:8080`

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-03T13:21:45.123456",
  "service": "YGG Torrent Authentication API"
}
```

### 2. Authentication
**POST** `/auth/login`

Authenticate and generate fresh cookies.

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "cookies": {
    "account_created": "true",
    "ygg_": "session_token",
    "cf_clearance": "cloudflare_token"
  },
  "cookie_string": "account_created=true; ygg_=token; cf_clearance=token",
  "generated_at": "2025-09-03T13:21:45.123456",
  "cookie_file": "data/api_cookies_20250903_132145.json"
}
```

### 3. Authentication Status
**GET** `/auth/status?cookies=<cookie_string>`

Check if cookies are still valid.

**Response:**
```json
{
  "success": true,
  "authenticated": true,
  "status_code": 200,
  "message": "Authenticated"
}
```

### 4. Get Categories
**GET** `/categories`

Get all available categories.

**Response:**
```json
{
  "success": true,
  "categories": {
    "2163": {
      "id": 2163,
      "name": "Nintendo",
      "parent_id": "2142",
      "parent_name": "Flux RSS sous-catégories",
      "item_count": 100,
      "rss_url": "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=YOUR_PASSKEY"
    }
  },
  "count": 50
}
```

### 5. Get RSS Feed
**GET** `/rss/<category_id>?cookies=<cookie_string>&passkey=<passkey>`

Get RSS feed for a specific category.

**Response:**
```json
{
  "success": true,
  "category_id": 2163,
  "torrents": [
    {
      "id": "1361503",
      "title": "[Mig Switch] Hogwarts Legacy v1.0.0 [EU] XCI",
      "link": "https://www.yggtorrent.top/torrent/jeux-video/switch/1361503-hogwarts-legacy",
      "category": "Nintendo"
    }
  ],
  "count": 100
}
```

## Usage Examples

### Python Client
```python
import requests

# Authenticate
response = requests.post('http://localhost:8080/auth/login', json={
    'username': 'your_username',
    'password': 'your_password'
})

if response.json()['success']:
    cookie_string = response.json()['cookie_string']
    
    # Get categories
    categories = requests.get('http://localhost:8080/categories')
    
    # Get RSS feed
    rss = requests.get(f'http://localhost:8080/rss/2163', params={
        'cookies': cookie_string,
        'passkey': 'your_passkey'
    })
```

### cURL Examples
```bash
# Health check
curl http://localhost:8080/health

# Authenticate
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# Check status
curl "http://localhost:8080/auth/status?cookies=your_cookie_string"

# Get categories
curl http://localhost:8080/categories

# Get RSS feed
curl "http://localhost:8080/rss/2163?cookies=your_cookie_string&passkey=your_passkey"
```

### JavaScript/Fetch
```javascript
// Authenticate
const authResponse = await fetch('http://localhost:8080/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'your_username',
    password: 'your_password'
  })
});

const authData = await authResponse.json();
if (authData.success) {
  const cookieString = authData.cookie_string;
  
  // Get RSS feed
  const rssResponse = await fetch(
    `http://localhost:8080/rss/2163?cookies=${encodeURIComponent(cookieString)}&passkey=your_passkey`
  );
  const rssData = await rssResponse.json();
}
```

## Testing

Use the included client script to test the API:

```bash
python3 ygg_api_client.py
```

## Configuration

- **Host**: `0.0.0.0` (accessible from any IP)
- **Port**: `8080`
- **Debug**: `False` (set to `True` for development)

## Security Notes

- The API runs on all interfaces (`0.0.0.0`) - consider firewall rules for production
- Credentials are sent in plain text - use HTTPS in production
- Cookies are stored temporarily in the `data/` directory
- Logs are written to `logs/api.log`

## Error Handling

All endpoints return JSON responses with a `success` field:

```json
{
  "success": false,
  "message": "Error description"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (missing parameters)
- `401` - Unauthorized (authentication failed)
- `404` - Not Found (endpoint not found)
- `500` - Internal Server Error

## Logs

API logs are written to `logs/api.log` and include:
- Authentication attempts
- API requests
- Errors and exceptions
- Cookie generation events
