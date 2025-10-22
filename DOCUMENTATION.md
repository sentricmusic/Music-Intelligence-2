# Music Intelligence Platform Documentation

## System Overview

The Music Intelligence Platform is a comprehensive data collection and analysis system that combines Spotify playlist discovery with Apple Music metadata enrichment. The platform features an advanced Cultural Intelligence Engine that automatically adapts to international markets and musical genres without requiring manual configuration.

## Architecture

### Backend Services

#### Cultural Intelligence Engine (simple_working.py)
- **Primary Server**: Flask application running on port 5001
- **Core Functionality**: Universal market and genre adaptation
- **Authentication**: Apple Music API with JWT token generation
- **Market Coverage**: 13+ international markets including France, Germany, Spain, UK, US, Thailand, Japan, Italy, Netherlands, Sweden, Norway, Brazil, Mexico, Australia, Canada, South Korea

#### Key Features
- **Native Language Search**: Automatic integration of local terminology and cultural context
- **Cross-Cultural Filtering**: Prevention of inappropriate genre contamination
- **IPI Extraction**: Comprehensive songwriter metadata extraction from Apple Music
- **Quality Scoring**: Advanced prioritization algorithms for authentic content discovery

### Frontend Interface

#### React Application (port 3000)
- **User Interface**: Modern React-based web interface
- **Real-time Results**: Live playlist discovery and analysis
- **Statistical Dashboard**: Comprehensive success rate tracking and IPI statistics
- **Cultural Intelligence Testing**: Interface for validating market-specific results

## API Endpoints

### Core Endpoints

#### POST /api/analyze
Analyzes market and genre combinations using cultural intelligence.

**Request Format:**
```json
{
  "market": "France",
  "genre": "hip-hop"
}
```

**Response Format:**
```json
{
  "success": true,
  "playlists": [
    {
      "name": "RAP FRANÇAIS 2025",
      "priority": 47,
      "tracks": 150,
      "owner": "Spotify",
      "followers": 125000,
      "cultural_authenticity": "high"
    }
  ]
}
```

#### POST /api/playlist-tracks
Retrieves tracks from discovered playlists with ISRC codes for Apple Music matching.

**Request Format:**
```json
{
  "playlist_urls": ["spotify:playlist:abc123"]
}
```

#### POST /api/writer-credits
Extracts comprehensive writer credits and IPI numbers from Apple Music.

**Request Format:**
```json
{
  "tracks": [
    {
      "track_name": "Fantasy",
      "track_artist": "Meiko Nakahara",
      "isrc": "JPTO08815590"
    }
  ]
}
```

**Response Format:**
```json
{
  "success": true,
  "stats": {
    "total_processed": 10,
    "found_in_apple_music": 8,
    "apple_music_success_rate": "80.0%",
    "total_ipis_found": 8,
    "artist_ipis_found": 7,
    "writer_ipis_found": 1,
    "ipi_success_rate": "80.0%"
  },
  "tracks": [
    {
      "track_name": "Fantasy",
      "main_artist_ipi": "259021134",
      "writer_ipis": [
        {
          "name": "Meiko Nakahara",
          "ipi": "259021134"
        }
      ]
    }
  ]
}
```

## Cultural Intelligence Configuration

### Market Configurations
The system includes comprehensive market-specific configurations that automatically activate based on user selections:

```python
market_config = {
    'France': {
        'code': 'FR',
        'terms': ['français', 'french', 'france', 'fr'],
        'genre_translations': {
            'hip-hop': ['rap français', 'rap fr', 'rappeur français'],
            'electronic': ['électro français', 'french electronic', 'électro fr']
        }
    },
    'Japan': {
        'code': 'JP',
        'terms': ['japan', 'japanese', 'jp', '日本'],
        'genre_translations': {
            'pop': ['j-pop', 'jpop', 'japanese pop', '日本のポップ'],
            'electronic': ['japanese electronic', 'j-electronic']
        }
    }
}
```

### Priority Scoring Algorithm
The system uses a sophisticated scoring mechanism to rank playlist authenticity:

- **Market-specific boost**: +20 points for local market terms
- **Genre translation boost**: +15 points for native language genre terms
- **Recency boost**: +8 points for current year content
- **Quality indicators**: +3-9 points for established quality markers
- **Mainstream balance**: Additional scoring for appropriate mainstream/underground balance

### Universal Filtering System
Prevents cross-cultural contamination while maintaining authenticity:

- **Genre Isolation**: Prevents K-pop from appearing in non-Korean searches
- **Language Filtering**: Maintains linguistic authenticity per market
- **Cultural Context**: Respects local music scene hierarchies and preferences
- **Quality Threshold**: Filters low-engagement or inappropriate content

## Apple Music Integration

### Authentication System
- **Team ID**: 2MQ6NB4Q3C (Production)
- **Key ID**: FH2F6F277R (Active)
- **Private Key**: AuthKey_FH2F6F277R.p8 (Secure storage)
- **JWT Generation**: Automatic token refresh with ES256 algorithm

### IPI Extraction Process
1. **ISRC Matching**: Search Apple Music catalog using provided ISRC codes
2. **URL Pattern Analysis**: Extract artist IPI numbers from Apple Music URLs using regex patterns
3. **Composer Search**: Secondary search for writer IPIs through composer metadata
4. **Comprehensive Aggregation**: Combine all extracted IPI data with success rate tracking

### Success Rate Tracking
The system provides detailed statistics on multiple extraction methods:

- **Traditional Writer Credits**: Apple Music composer field data
- **Artist IPI Extraction**: Main artist IPI numbers from URL patterns
- **Writer IPI Extraction**: Songwriter IPI numbers from composer searches
- **Overall IPI Success Rate**: Combined success across all extraction methods

## Performance and Rate Limiting

### Request Management
- **Apple Music API**: 0.5-second delays between requests to respect rate limits
- **Spotify API**: Standard rate limiting with automatic retry mechanisms
- **Processing Limits**: 10-track limit for development testing, scalable to full playlist processing
- **Error Handling**: Comprehensive exception management with detailed error reporting

### Response Optimization
- **Cultural Prioritization**: Results ordered by cultural authenticity scores
- **Pagination Support**: Efficient handling of large playlist collections
- **Caching Strategy**: Intelligent caching of market configurations and search patterns
- **Memory Management**: Optimized data structures for large-scale processing

## Quality Assurance

### Validation Results
The system has been extensively tested across multiple market/genre combinations:

#### France Hip-Hop Validation
- **Search Query**: "rap français FR"
- **Result**: "RAP FRANÇAIS 2025" (authentic French rap content)
- **Cultural Filter**: Successfully blocks K-pop, J-pop, and lofi contamination
- **Priority Score**: 47 (native language + recency + quality indicators)

#### UK Electronic Validation
- **Search Query**: "UK dance hits 2025"
- **Results**: "CAPITAL DANCE", "UK DANCE CHARTS 2025"
- **Cultural Balance**: Appropriate mix of mainstream (Altar, UK House) and underground (UK Garage)
- **Priority Score**: 42 (market + genre + mainstream boost)

#### Japan Pop Validation
- **Search Query**: "J-pop japan JP"
- **Result**: "80年代の邦楽" (629K saves, native Japanese titles)
- **Cultural Authenticity**: Native Japanese content with historical period accuracy
- **Priority Score**: 45 (cultural authenticity + massive engagement)

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Valid Spotify API credentials
- Apple Music API credentials (Team ID, Key ID, Private Key)

### Backend Setup
1. Navigate to the backend directory
2. Install Python dependencies: `pip install flask flask-cors requests python-dotenv pyjwt`
3. Configure environment variables in .env file
4. Place Apple Music private key file in backend directory
5. Start server: `python simple_working.py`

### Frontend Setup
1. Navigate to project root directory
2. Install Node.js dependencies: `npm install`
3. Start development server: `npm start`
4. Access application at http://localhost:3000

### Environment Configuration
Create a .env file in the backend directory:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

Ensure Apple Music credentials are properly configured:
- AuthKey_FH2F6F277R.p8 file in backend directory
- Correct Team ID and Key ID in simple_working.py

## Troubleshooting

### Common Issues

#### Backend Server Fails to Start
- Verify Python dependencies are installed
- Check .env file configuration
- Ensure Apple Music private key file exists
- Confirm port 5001 is available

#### Frontend Connection Issues
- Verify backend server is running on port 5001
- Check CORS configuration in Flask application
- Confirm React application is accessible on port 3000

#### Apple Music Authentication Errors
- Validate Team ID and Key ID configuration
- Check private key file permissions and location
- Verify JWT token generation is working correctly

#### Cultural Intelligence Results Issues
- Confirm market and genre parameters are properly formatted
- Check cultural filtering configuration for target market
- Verify priority scoring algorithm is functioning correctly

## Development and Extension

### Adding New Markets
1. Add market configuration to market_config dictionary
2. Include native language terms and genre translations
3. Configure appropriate cultural filtering rules
4. Test with representative genre combinations

### Enhancing Cultural Intelligence
1. Expand genre translation mappings for existing markets
2. Implement additional cultural context indicators
3. Refine priority scoring algorithms based on market feedback
4. Add support for regional music scene hierarchies

### Performance Optimization
1. Implement caching for frequent market/genre combinations
2. Optimize database queries for large-scale processing
3. Add asynchronous processing for bulk operations
4. Implement advanced error recovery mechanisms

## Security Considerations

### API Key Management
- Store sensitive credentials in environment variables
- Use secure file permissions for private key files
- Implement proper access controls for production deployment
- Regular rotation of API credentials as per provider requirements

### Data Protection
- Implement appropriate data retention policies
- Secure handling of user playlist and track data
- Compliance with relevant privacy regulations
- Audit logging for sensitive operations

## Support and Maintenance

### Monitoring
- Regular validation of cultural intelligence accuracy
- Performance monitoring of API response times
- Success rate tracking across different markets
- Error rate analysis and resolution

### Updates and Maintenance
- Regular updates to market configurations based on cultural evolution
- Monitoring of streaming platform API changes
- Performance optimization based on usage patterns
- Security updates and dependency management