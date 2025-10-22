# Quick Start Guide

## System Prerequisites
- Node.js and npm installed
- Python 3.8+ installed  
- Valid Spotify API credentials
- Apple Music API credentials (Team ID, Key ID, Private Key)

## Universal Music Intelligence Platform

### Instant Cultural Intelligence Setup

#### 1. Start Universal Discovery Engine (Terminal 1)
```powershell
cd "C:\Users\kaz.roche\Desktop\music-intelligence\backend"
python simple_working.py
```
This loads the advanced cultural intelligence system for all international markets.

#### 2. Start Frontend Interface (Terminal 2) 
```powershell
cd "C:\Users\kaz.roche\Desktop\music-intelligence"
npm start
```

#### 3. Port Conflict Resolution (if needed)
```powershell
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F
npm start
```

## Testing Workflow

### Cultural Intelligence Validation
1. Open: http://localhost:3000
2. Test Market/Genre Combinations:
   - France + Hip-Hop: Expected results include "RAP FRANÇAIS 2025", authentic French rap content
   - UK + Electronic: Expected results include "UK DANCE CHARTS", "CAPITAL DANCE", UK garage content
   - Japan + Pop: Expected results include "80年代の邦楽", native Japanese content with cultural authenticity
   - Germany + Hip-Hop: Expected results include "deutscher rap" content with German cultural context
   - Any Market + Genre: System provides automatic cultural adaptation

### Advanced Writer Credits Analysis (Apple Music Integration)
3. Select any discovered playlist and click "Load Tracks" 
4. Click "Get Writer Credits (Apple Music)" to initiate comprehensive metadata extraction
5. Verify output includes IPI numbers and detailed songwriter metadata

## Cultural Intelligence Features

### Core Capabilities
- Native Language Search: Automatic integration of local terminology ("rap français", "deutscher rap", "日本の音楽")
- Cross-Cultural Filtering: Prevention of inappropriate content mixing (no K-pop in French searches, no lofi in rap results)
- Quality Intelligence: Prioritization of authentic, high-engagement playlists based on cultural relevance
- Universal Coverage: Comprehensive support for France, UK, Germany, Spain, Japan, Italy, Brazil, and additional international markets
- Mainstream Balance: Optimal combination of underground authenticity with accessible mainstream content

### Technical Architecture
- Server: backend/simple_working.py (Universal Cultural Engine)
- Market Intelligence: 13+ international markets with automatic cultural adaptation
- Apple Music Integration: Production credentials with comprehensive IPI extraction capabilities
- Quality Assurance: Advanced cultural accuracy validation and music intelligence analysis

## Expected System Performance

### Cultural Accuracy Metrics
- Cultural Accuracy: Authentic market-specific playlist discovery and analysis
- Apple Music Integration: Production-ready system with comprehensive IPI extraction functionality
- Universal Coverage: Automatic adaptation for any market/genre combination without manual configuration
- Zero Configuration: No manual setup required for new market integration

### Performance Validation
The system provides detailed success tracking across multiple dimensions:
- Apple Music API integration success rates
- IPI extraction performance for both artist and writer identification
- Cultural authenticity scoring mechanisms
- Market-specific quality indicator analysis

This platform represents an advanced implementation of universal music cultural intelligence for international discovery and comprehensive analysis applications.