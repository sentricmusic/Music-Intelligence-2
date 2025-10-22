# Luminate Data Specification

## Overview
This document defines the structure, logic, and usage patterns for Luminate streaming data integration in the Universal Cultural Intelligence system.

## Data Source
- **Database**: `RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING`
- **Update Frequency**: Monthly
- **Coverage**: Top 50,000 recordings globally
- **Territories**: 18 individual territories + WW (Worldwide)

## Data Structure

### Key Fields for Integration
| Field | Type | Description | Usage |
|-------|------|-------------|-------|
| `ISRC` | VARCHAR | International Standard Recording Code | **PRIMARY JOIN KEY** with Spotify/Apple Music data |
| `Streams ATD` | NUMBER | All-Time-to-Date total streams | **PRIMARY METRIC** for baseline streaming |
| `Territory` | VARCHAR | Market code (e.g., "US", "UK", "WW") | Territory-specific analysis |
| `Activity Year` | VARCHAR | Year of data (e.g., "2024") | Time series analysis |
| `Activity Month` | VARCHAR | Month name (e.g., "January") | Monthly tracking |

### Streaming Breakdown Fields
| Field | Description | Analysis Use |
|-------|-------------|--------------|
| `Streams` | Monthly streams for that territory | Growth tracking |
| `Ad-Supported` | Free tier streaming | User behavior analysis |
| `Premium` | Paid tier streaming | Revenue analysis |
| `On-Demand` | User-initiated plays | Engagement quality |
| `Programmed` | Algorithm/radio plays | Platform promotion |

### Additional Metrics
| Field | Description | Intelligence Value |
|-------|-------------|-------------------|
| `Airplay Spins` | Radio play count | Radio crossover tracking |
| `Airplay Audience` | Radio reach | Mainstream penetration |
| `Song Sales` | Digital/physical sales | Commercial performance |
| `Luminate Genres` | Genre classification | Genre analysis |

## Critical Logic: Total Streams Calculation

### The Challenge
- **Top 50K Limit**: Tracks drop in/out of reports based on popularity
- **Territory Fragmentation**: Popular tracks may appear in multiple territories
- **WW vs Territory Data**: Worldwide data takes priority when available

### Solution Algorithm

```sql
-- Step 1: Check for Worldwide (WW) data first
SELECT MAX(streams_atd) as total_streams
FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
WHERE ISRC = '{target_isrc}' 
  AND Territory = 'WW'

-- Step 2: If no WW data, aggregate all territories
SELECT SUM(max_streams_per_territory) as total_streams
FROM (
    SELECT Territory, MAX(streams_atd) as max_streams_per_territory
    FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
    WHERE ISRC = '{target_isrc}' 
      AND Territory != 'WW'
    GROUP BY Territory
)
```

### Implementation Logic
1. **Priority Check**: Always query WW territory first
2. **Fallback Aggregation**: If no WW data exists, sum MAX streams from all individual territories
3. **Territory Deduplication**: Use MAX() per territory to avoid double-counting across months
4. **Result**: Single total streams number for baseline analysis

## Data Quality Considerations

### Coverage Limitations
- **Top 50K Only**: Niche tracks may not appear consistently
- **Monthly Reporting**: No real-time data
- **Territory Gaps**: Some tracks may only appear in specific markets

### Data Reliability
- **WW Data Priority**: Most accurate for global tracks
- **Territory Summation**: Good approximation for regional hits
- **Historical Tracking**: Monthly snapshots enable growth analysis

## Integration Points

### Universal Cultural Intelligence Pipeline
1. **Discovery Phase**: Spotify API → Extract tracks with ISRC
2. **Credit Intelligence**: Apple Music API → Writer credits + IPIs
3. **→ Streaming Intelligence**: Luminate → Baseline streams + growth metrics ← **THIS PHASE**
4. **Market Analysis**: Growth tracking, crossover detection

### Key Metrics to Extract
- **Baseline Streams**: Total streams at discovery
- **Territory Breakdown**: Where the track is popular
- **Stream Quality**: Premium vs Ad-supported ratio
- **Radio Performance**: Airplay spins and audience
- **Growth Indicators**: Monthly progression data

## Example Data Records

### Worldwide Record
```json
{
  "ISRC": "USRC12301932",
  "Title": "greedy",
  "Display Artist": "Tate McRae",
  "Territory": "WW",
  "Streams ATD": 890000000,
  "Activity Year": "2024",
  "Activity Month": "October"
}
```

### Territory-Specific Record
```json
{
  "ISRC": "TCAGM2208561", 
  "Title": "Si No Estás",
  "Display Artist": "iñigo quintero",
  "Territory": "CH",
  "Streams ATD": 7950292,
  "Premium": 1079587,
  "Ad-Supported": 488992
}
```

## Future Enhancements

### Growth Analysis Capabilities
- **30/60/90 Day Growth**: Compare monthly streams progression
- **Territory Expansion**: Track when songs break into new markets
- **Crossover Detection**: Identify genre-to-mainstream transitions
- **Playlist Impact**: Correlate playlist adds with streaming spikes

### Market Intelligence
- **Drive Time Analysis**: Cross-reference with radio airplay timing
- **Premium Ratio**: Quality engagement metrics per territory
- **Genre Migration**: Track when niche tracks gain mainstream traction

## Implementation Notes
- **Database Connection**: Requires Snowflake/SQL connection to Luminate DB
- **Rate Limiting**: Monthly data means no real-time constraints
- **Caching Strategy**: Cache results per ISRC to avoid repeated queries
- **Error Handling**: Graceful fallback when no Luminate data exists

---
*This specification ensures consistent implementation and prevents misunderstandings about Luminate data usage in the Universal Cultural Intelligence system.*