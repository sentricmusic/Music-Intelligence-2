# API Reference Documentation

## Base URL
```
Backend API: http://localhost:5001
Frontend UI: http://localhost:3000
```

## Authentication
The system uses Apple Music JWT authentication for API access. Authentication is handled automatically by the backend service.

## Endpoints

### Cultural Intelligence Analysis

#### POST /api/analyze
Performs cultural intelligence analysis for market and genre combinations.

**Request Body:**
```json
{
  "market": "string",
  "genre": "string"
}
```

**Supported Markets:**
- France, Germany, Spain, UK, US, Thailand, Japan, Italy, Netherlands, Sweden, Norway, Brazil, Mexico, Australia, Canada, South Korea

**Supported Genres:**
- hip-hop, electronic, pop, rock, jazz, classical, country, reggae, blues, folk

**Response:**
```json
{
  "success": true,
  "playlists": [
    {
      "name": "string",
      "description": "string",
      "priority": "number",
      "tracks": "number",
      "owner": "string",
      "followers": "number",
      "url": "string",
      "cultural_authenticity": "string"
    }
  ],
  "cultural_intelligence": {
    "market_terms_used": ["string"],
    "native_language_queries": ["string"],
    "filtering_applied": ["string"]
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"market": "France", "genre": "hip-hop"}'
```

**Example Response:**
```json
{
  "success": true,
  "playlists": [
    {
      "name": "RAP FRANÇAIS 2025",
      "description": "Les meilleurs titres du rap français",
      "priority": 47,
      "tracks": 150,
      "owner": "Spotify",
      "followers": 125000,
      "url": "https://open.spotify.com/playlist/abc123",
      "cultural_authenticity": "high"
    }
  ],
  "cultural_intelligence": {
    "market_terms_used": ["français", "french", "france"],
    "native_language_queries": ["rap français FR", "rappeur français"],
    "filtering_applied": ["kpop", "jpop", "lofi"]
  }
}
```

### Playlist Track Extraction

#### POST /api/playlist-tracks
Extracts tracks from discovered playlists with ISRC codes for Apple Music integration.

**Request Body:**
```json
{
  "playlist_urls": ["string"]
}
```

**Response:**
```json
{
  "success": true,
  "tracks": [
    {
      "track_name": "string",
      "track_artist": "string",
      "album_name": "string",
      "isrc": "string",
      "popularity": "number",
      "release_date": "string",
      "playlist_source": "string"
    }
  ],
  "statistics": {
    "total_tracks": "number",
    "tracks_with_isrc": "number",
    "isrc_success_rate": "string"
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5001/api/playlist-tracks \
  -H "Content-Type: application/json" \
  -d '{"playlist_urls": ["https://open.spotify.com/playlist/abc123"]}'
```

### Apple Music Writer Credits

#### POST /api/writer-credits
Extracts comprehensive writer credits and IPI numbers from Apple Music.

**Request Body:**
```json
{
  "tracks": [
    {
      "track_name": "string",
      "track_artist": "string",
      "isrc": "string"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_processed": "number",
    "has_isrc": "number",
    "found_in_apple_music": "number",
    "has_writer_credits": "number",
    "apple_music_success_rate": "string",
    "writer_credits_rate": "string",
    "total_ipis_found": "number",
    "artist_ipis_found": "number",
    "writer_ipis_found": "number",
    "ipi_success_rate": "string",
    "has_any_ipis": "number"
  },
  "tracks": [
    {
      "track_name": "string",
      "track_artist": "string",
      "album_name": "string",
      "isrc": "string",
      "api_status": "string",
      "composer_names": ["string"],
      "main_artist_ipi": "string",
      "writer_ipis": [
        {
          "name": "string",
          "ipi": "string"
        }
      ],
      "apple_music_url": "string",
      "popularity": "number",
      "release_date": "string"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5001/api/writer-credits \
  -H "Content-Type: application/json" \
  -d '{
    "tracks": [
      {
        "track_name": "Fantasy",
        "track_artist": "Meiko Nakahara",
        "isrc": "JPTO08815590"
      }
    ]
  }'
```

**Example Response:**
```json
{
  "success": true,
  "stats": {
    "total_processed": 1,
    "has_isrc": 1,
    "found_in_apple_music": 1,
    "has_writer_credits": 1,
    "apple_music_success_rate": "100.0%",
    "writer_credits_rate": "100.0%",
    "total_ipis_found": 1,
    "artist_ipis_found": 1,
    "writer_ipis_found": 0,
    "ipi_success_rate": "100.0%",
    "has_any_ipis": 1
  },
  "tracks": [
    {
      "track_name": "Fantasy",
      "track_artist": "Meiko Nakahara",
      "album_name": "Orient",
      "isrc": "JPTO08815590",
      "api_status": "found_with_credits",
      "composer_names": ["Meiko Nakahara"],
      "main_artist_ipi": "259021134",
      "writer_ipis": [],
      "apple_music_url": "https://music.apple.com/us/album/fantasy/259021134",
      "popularity": 56,
      "release_date": "1982-12-21"
    }
  ]
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": "string",
  "error_code": "string",
  "details": "object"
}
```

### Common Error Codes

#### 400 Bad Request
- **INVALID_MARKET**: Unsupported market specified
- **INVALID_GENRE**: Unsupported genre specified  
- **MISSING_PARAMETERS**: Required parameters not provided
- **INVALID_JSON**: Request body contains invalid JSON

#### 401 Unauthorized
- **APPLE_MUSIC_AUTH_FAILED**: Apple Music authentication failure
- **SPOTIFY_AUTH_FAILED**: Spotify authentication failure

#### 429 Too Many Requests
- **RATE_LIMIT_EXCEEDED**: API rate limit exceeded
- **APPLE_MUSIC_QUOTA**: Apple Music API quota exceeded

#### 500 Internal Server Error
- **CULTURAL_INTELLIGENCE_ERROR**: Cultural intelligence processing failure
- **DATABASE_ERROR**: Database operation failure
- **EXTERNAL_API_ERROR**: External API integration error

## Rate Limiting

### Request Limits
- **Apple Music API**: 0.5-second minimum interval between requests
- **Spotify API**: Standard rate limiting with automatic retry
- **Cultural Intelligence**: No specific limits, performance optimized

### Best Practices
- Implement appropriate delays between bulk requests
- Use batch processing for large datasets
- Monitor response headers for rate limit information
- Implement exponential backoff for failed requests

## Cultural Intelligence Parameters

### Market Configuration
Each market includes comprehensive cultural intelligence:

```json
{
  "market_code": "string",
  "native_terms": ["string"],
  "genre_translations": {
    "genre": ["string"]
  },
  "cultural_filters": ["string"],
  "quality_indicators": ["string"]
}
```

### Priority Scoring Factors
- Market-specific terminology presence: +20 points
- Native language genre terms: +15 points  
- Content recency indicators: +8 points
- Quality and engagement markers: +3-9 points
- Cultural authenticity validation: Variable scoring

### Filtering Categories
- **Cross-cultural contamination prevention**
- **Quality threshold enforcement** 
- **Language authenticity maintenance**
- **Genre purity preservation**

## Data Types and Validation

### Market Values
```
Enum: ["France", "Germany", "Spain", "UK", "US", "Thailand", "Japan", 
       "Italy", "Netherlands", "Sweden", "Norway", "Brazil", "Mexico", 
       "Australia", "Canada", "South Korea"]
```

### Genre Values
```
Enum: ["hip-hop", "electronic", "pop", "rock", "jazz", "classical", 
       "country", "reggae", "blues", "folk"]
```

### ISRC Format
```
Pattern: ^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$
Example: "USRC12301954"
```

### IPI Format
```
Pattern: ^\d{9,11}$
Example: "259021134"
```

## Integration Examples

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:5001/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    market: 'France',
    genre: 'hip-hop'
  })
});

const data = await response.json();
console.log(data.playlists);
```

### Python
```python
import requests

response = requests.post(
    'http://localhost:5001/api/analyze',
    json={'market': 'France', 'genre': 'hip-hop'}
)

data = response.json()
print(data['playlists'])
```

### curl
```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"market": "France", "genre": "hip-hop"}'
```

## Performance Considerations

### Response Times
- Cultural intelligence analysis: 2-5 seconds
- Playlist track extraction: 1-3 seconds per playlist
- Apple Music writer credits: 0.5-1 second per track

### Optimization Strategies
- Implement caching for frequent market/genre combinations
- Use pagination for large result sets
- Batch process multiple requests when possible
- Monitor and optimize cultural intelligence algorithms

### Scalability Features
- Asynchronous processing capabilities
- Configurable processing limits
- Advanced error recovery mechanisms
- Comprehensive logging and monitoring