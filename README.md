# 🎵 Music Intelligence - Predictive Analytics Platform

A comprehensive data collection and analysis platform for music streaming intelligence, combining Spotify playlist analysis with Apple Music metadata enrichment to build predictive models for music industry insights.

## 🎯 Project Goals

### Primary Objective
Build a **Predictive Music Intelligence System** that combines multi-platform streaming data to identify trending tracks, emerging artists, and market patterns before they hit mainstream charts.

### Key Use Cases
- **A&R Intelligence**: Discover unsigned artists gaining traction across markets
- **Playlist Strategy**: Understand what makes playlists successful in different regions  
- **Market Analysis**: Compare genre performance across 7 major music markets
- **Trend Prediction**: Identify tracks with viral potential using combined metadata
- **Writer Credits Analysis**: Track songwriter and producer success patterns

## 🏗️ System Architecture

### Phase 1: Multi-Platform Data Collection ✅
**Current Implementation Status: COMPLETE**

#### Spotify Web API Integration
- **Multi-Language Search Strategy**: Searches using market codes, genre terms, and full market names
- **Market Coverage**: France, UK, Germany, Spain, US, Thailand, Japan
- **Genre Analysis**: Hip-Hop, Pop, Electronic, R&B, Rock
- **Comprehensive Data Schema**:
  ```
  playlist_name, playlist_id, playlist_followers, track_name, track_artist, 
  track_added_at, track_release_date, track_popularity, isrc, spotify_link
  ```

#### Apple Music API Integration 🆕
- **Writer Credits Extraction**: Pulls songwriter/producer information via ISRC matching
- **Enhanced Metadata**: Combines Spotify streaming data with Apple Music compositional data
- **JWT Authentication**: Secure token-based Apple Music API access

### Phase 2: Data Warehouse Integration (Planned)
- **Snowflake Integration**: Push collected data to enterprise data warehouse
- **Historical Analysis**: Compare current trends with historical patterns
- **Luminate Data Connection**: Integrate industry-standard chart and sales data

### Phase 3: Predictive Modeling (Roadmap)
- **Machine Learning Pipeline**: Build models to predict track success
- **Market-Specific Models**: Separate prediction algorithms for each geographic market
- **Real-Time Scoring**: Live assessment of new track viral potential

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v14+ recommended)
- **Python** (v3.8+ required)  
- **Spotify Developer Account** with Client ID/Secret
- **Apple Music API Credentials** (Team ID, Key ID, Private Key)

### Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/sentricmusic/music-intelligence.git
   cd music-intelligence
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install flask flask-cors requests python-dotenv PyJWT
   ```

4. Configure environment variables:
   ```bash
   # Create backend/.env file
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   ```

5. Add Apple Music credentials to `backend/app.py`:
   ```python
   APPLE_TEAM_ID = "your_team_id"
   APPLE_KEY_ID = "your_key_id"  
   APPLE_PRIVATE_KEY_PATH = "path/to/AuthKey.p8"
   ```

### Running the Application
1. **Start Backend Server**:
   ```bash
   cd backend
   python app.py
   # Server runs on http://localhost:5000
   ```

2. **Start Frontend Application**:
   ```bash
   npm start
   # App opens at http://localhost:3000 (or 3001 if 3000 is busy)
   ```

## 🔧 API Endpoints

### Core Data Collection
- **POST `/api/analyze`** - Discover playlists by market and genre
- **POST `/api/playlist-tracks`** - Extract detailed track data from playlists
- **POST `/api/enrich-tracks`** 🆕 - Enrich Spotify data with Apple Music writer credits

### Request/Response Examples
```javascript
// Analyze French Hip-Hop Market
POST /api/analyze
{
  "market": "France",
  "genre": "Hip-Hop"
}

// Response: Top playlists with follower counts and metadata
{
  "success": true,
  "playlists_found": 47,
  "playlists": [...], // Top 10 playlists with full metadata
  "market": "France",
  "genre": "Hip-Hop"
}
```

## 📊 Data Schema & Output

### Spotify Track Data
```json
{
  "playlist_name": "FRENCH RAP 2025🇫🇷",
  "playlist_id": "37i9dQZF1DX0XUsuxWHRQd", 
  "playlist_followers": 47909,
  "track_name": "KYKY2BONDY",
  "track_artist": "Hamza",
  "track_added_at": "2025-06-25",
  "track_release_date": "2025-06-20",
  "track_popularity": 70,
  "isrc": "BEGCM2500005",
  "spotify_link": "https://open.spotify.com/track/..."
}
```

### Enhanced Apple Music Data 🆕
```json
{
  // ... all Spotify fields above ...
  "writers": ["Hamza Al-Farissi", "Producer Name"],
  "writer_count": 2
}
```

## 🌍 Multi-Market Intelligence

### Supported Markets
| Market | Code | Language Strategy | Genre Focus |
|---------|------|------------------|-------------|
| 🇫🇷 France | FR | French + English terms | Hip-Hop dominant |
| 🇬🇧 UK | GB | English variants | Pop + Electronic |  
| 🇩🇪 Germany | DE | German + English | Electronic + Pop |
| 🇪🇸 Spain | ES | Spanish terms | Pop + Latin |
| 🇺🇸 US | US | English (global) | All genres |
| 🇹🇭 Thailand | TH | Thai + English | Pop + Electronic |
| 🇯🇵 Japan | JP | Japanese + Romaji | Pop + Rock |

### Search Strategy Innovation
The platform uses a **3-tier search approach** to maximize playlist discovery:

1. **Market Code + Genre**: `"FR hip-hop"` - Catches local/regional playlists
2. **Genre Only**: `"hip-hop"` - Finds major international playlists  
3. **Full Market Name**: `"france hip-hop"` - Discovers English-titled playlists with local content

This approach solved the critical issue where Japan Pop searches were missing major English-titled playlists containing Japanese artists.

## 📁 Project Structure

```
music-intelligence/
├── src/                    # React frontend application
│   ├── App.js             # Main UI with dynamic layouts
│   ├── App.css            # Styling and responsive design
│   └── sentric-logo.png   # Sentric Music branding
├── backend/               # Flask API server
│   ├── app.py            # Multi-API integration (Spotify + Apple Music)
│   └── .env              # Environment variables (not committed)
├── versions/             # Version control for major releases
│   └── v1.0-spotify-complete/  # Backup of Spotify-only implementation
├── Visual Studio Apple/  # Apple Music API reference implementation
└── public/              # Static assets
```

## 🚧 Development Phases

### ✅ Phase 1: Foundation (Complete)
- [x] Spotify Web API integration with client credentials flow
- [x] Multi-market playlist discovery with 3-tier search strategy  
- [x] Comprehensive track metadata extraction with pagination
- [x] Professional React UI with dynamic layouts
- [x] Apple Music API integration for writer credits
- [x] JWT-based authentication for Apple Music

### 🔄 Phase 2: Data Pipeline (In Progress)
- [ ] Snowflake data warehouse integration
- [ ] Automated data collection scheduling  
- [ ] Data quality validation and cleansing
- [ ] Historical trend analysis capabilities

### 📈 Phase 3: Intelligence Layer (Planned)
- [ ] Machine learning model development
- [ ] Predictive scoring algorithms
- [ ] Real-time trend detection
- [ ] Market comparison analytics
- [ ] A&R recommendation engine

## 🤝 Contributing

### Development Workflow
1. **Feature Branches**: Create feature branches for new functionality
2. **Version Control**: Major releases are backed up in `versions/` directory
3. **Testing**: Validate against multiple markets before merging
4. **Documentation**: Update README for significant changes

### Current Branch Strategy
- `main`: Stable releases with full Spotify + Apple Music integration
- `feature/writer-credits`: Apple Music enhancement branch
- `versions/v1.0-spotify-complete`: Spotify-only backup for rollback

## 📞 Support & Contact

**Sentric Music Team**
- **Platform**: Music Intelligence & Analytics
- **Technical Lead**: Advanced AI Development
- **API Integration**: Spotify Web API, Apple Music API
- **Data Pipeline**: Snowflake, Luminate Integration

---

## 🔮 Vision: The Future of Music Intelligence

This platform represents the foundation of **next-generation music industry analytics**. By combining real-time streaming data with comprehensive metadata, we're building the tools that will help:

- **Record Labels** discover talent before competitors
- **Playlist Curators** understand what drives engagement  
- **Artists & Managers** time releases for maximum impact
- **Music Publishers** track writer/producer success patterns
- **Industry Analysts** predict market trends with data-driven insights

**The goal**: Transform music discovery from intuition-based to intelligence-driven, giving industry professionals the data advantage they need to succeed in an increasingly competitive landscape.

---

*Built with ❤️ for the music industry by the Sentric Music team*
