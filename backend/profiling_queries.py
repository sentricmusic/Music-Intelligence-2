"""
Profiling queries for market/genre analysis
All queries adapted for LUMINATEMONTHLYSTREAMSBYRECORDING schema
"""

def get_hit_songs_base_query(market_code):
    """
    Base CTE to identify all 5-50M hit songs in a market
    Used by most other queries
    """
    return f"""
    WITH hit_songs_5_50m AS (
        SELECT DISTINCT ISRC
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
        WHERE Territory = '{market_code}'
        GROUP BY ISRC
        HAVING MAX("Streams ATD") BETWEEN 5000000 AND 50000000
    )
    """


# ============================================================================
# QUERY 1: PLAYLIST PERFORMANCE + ACTIVITY
# ============================================================================
def get_playlist_performance_query(market_code, genre):
    """
    Returns top playlists by hit rate, combined with activity metrics
    
    Outputs:
    - playlist_name
    - total_songs (ever added)
    - songs_hit_5_50m (count)
    - hit_rate_5_50m_percent (success rate)
    - followers
    - avg_song_streams_millions
    - last_song_added (date)
    - days_since_last_update
    - avg_songs_per_month
    - activity_status (Very Active / Active / Moderate / Low / Inactive)
    - ml_model_priority (High / Medium / Low / Deprioritize)
    """
    return f"""
    WITH hit_songs_5_50m AS (
        SELECT DISTINCT ISRC
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
        WHERE Territory = '{market_code}'
        GROUP BY ISRC
        HAVING MAX("Streams ATD") BETWEEN 5000000 AND 50000000
    ),
    
    playlist_performance AS (
        SELECT 
            high_value.playlist_name,
            high_value.playlist_id,
            COUNT(DISTINCT high_value.isrc) as total_songs,
            COUNT(DISTINCT CASE WHEN hs.ISRC IS NOT NULL THEN high_value.isrc END) as songs_hit_5_50m,
            ROUND(
                COUNT(DISTINCT CASE WHEN hs.ISRC IS NOT NULL THEN high_value.isrc END) * 1.0 /
                NULLIF(COUNT(DISTINCT high_value.isrc), 0), 3
            ) as hit_rate_5_50m_percent,
            AVG(p.playlist_popularity) as avg_playlist_popularity,
            AVG(l."Streams ATD") as avg_song_streams
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.SPOTHIGHVALUE_ISRCS high_value
        LEFT JOIN RIGHTSAPP_INSIGHTS.PUBLIC.SPOTIFY_PLAYLIST_DATA p 
            ON high_value.isrc = p.isrc AND high_value.playlist_id = p.playlist_id
        LEFT JOIN (
            SELECT ISRC, MAX("Streams ATD") as "Streams ATD"
            FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
            WHERE Territory = '{market_code}'
            GROUP BY ISRC
        ) l ON high_value.isrc = l.ISRC
        LEFT JOIN hit_songs_5_50m hs ON high_value.isrc = hs.ISRC
        WHERE TRY_TO_DATE(p.added_at) <= CURRENT_DATE()
        AND l."Streams ATD" IS NOT NULL
        GROUP BY high_value.playlist_name, high_value.playlist_id
        HAVING COUNT(DISTINCT high_value.isrc) >= 10
    ),
    
    playlist_activity AS (
        SELECT 
            playlist_name,
            MAX(TRY_TO_DATE(added_at)) as last_song_added,
            DATEDIFF('day', MAX(TRY_TO_DATE(added_at)), CURRENT_DATE()) as days_since_last_update,
            COUNT(DISTINCT isrc) as total_songs_ever_added,
            DATEDIFF('month', MIN(TRY_TO_DATE(added_at)), MAX(TRY_TO_DATE(added_at))) as months_active
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.SPOTIFY_PLAYLIST_DATA
        WHERE TRY_TO_DATE(added_at) IS NOT NULL
        GROUP BY playlist_name
    )
    
    SELECT 
        pp.playlist_name,
        pp.total_songs,
        pp.songs_hit_5_50m,
        pp.hit_rate_5_50m_percent,
        CONCAT(ROUND(pp.avg_playlist_popularity/1000000, 1), 'M') as followers,
        ROUND(pp.avg_song_streams/1000000, 1) as avg_song_streams_millions,
        pa.last_song_added,
        pa.days_since_last_update,
        CASE 
            WHEN pa.months_active = 0 THEN pa.total_songs_ever_added
            ELSE ROUND(pa.total_songs_ever_added * 1.0 / GREATEST(pa.months_active, 1), 1)
        END as avg_songs_per_month,
        CASE 
            WHEN pa.days_since_last_update <= 7 THEN 'Very Active'
            WHEN pa.days_since_last_update <= 30 THEN 'Active'
            WHEN pa.days_since_last_update <= 90 THEN 'Moderate'
            WHEN pa.days_since_last_update <= 180 THEN 'Low Activity'
            ELSE 'Inactive'
        END as activity_status,
        CASE 
            WHEN pa.days_since_last_update <= 30 AND pp.hit_rate_5_50m_percent >= 0.20 THEN 'High Priority'
            WHEN pa.days_since_last_update <= 90 AND pp.hit_rate_5_50m_percent >= 0.15 THEN 'Medium Priority'
            WHEN pa.days_since_last_update <= 180 AND pp.hit_rate_5_50m_percent >= 0.10 THEN 'Low Priority'
            ELSE 'Deprioritize'
        END as ml_model_priority
    FROM playlist_performance pp
    LEFT JOIN playlist_activity pa ON pp.playlist_name = pa.playlist_name
    WHERE pa.last_song_added IS NOT NULL
    ORDER BY 
        CASE 
            WHEN pa.days_since_last_update <= 30 AND pp.hit_rate_5_50m_percent >= 0.20 THEN 1
            WHEN pa.days_since_last_update <= 90 AND pp.hit_rate_5_50m_percent >= 0.15 THEN 2
            WHEN pa.days_since_last_update <= 180 AND pp.hit_rate_5_50m_percent >= 0.10 THEN 3
            ELSE 4
        END,
        pp.hit_rate_5_50m_percent DESC
    LIMIT 50;
    """


# ============================================================================
# QUERY 2: TIMING ANALYSIS - Months to 5M
# ============================================================================
def get_timing_analysis_query(market_code, genre):
    """
    Analyzes how long it takes songs to reach 5M streams
    
    Outputs:
    - time_to_5m (category: 1-3 months, 4-6 months, 7-12 months, Over 1 year)
    - song_count
    - percentage
    - avg_final_streams_millions
    """
    return f"""
    WITH hit_songs_5_50m AS (
        SELECT DISTINCT ISRC
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
        WHERE Territory = '{market_code}'
        GROUP BY ISRC
        HAVING MAX("Streams ATD") BETWEEN 5000000 AND 50000000
    ),
    
    playlist_songs AS (
        SELECT DISTINCT 
            high_value.isrc,
            p.name as song_name,
            p.artist,
            MIN(TRY_TO_DATE(p.added_at)) as first_playlist_date
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.SPOTHIGHVALUE_ISRCS high_value
        LEFT JOIN RIGHTSAPP_INSIGHTS.PUBLIC.SPOTIFY_PLAYLIST_DATA p 
            ON high_value.isrc = p.isrc AND high_value.playlist_id = p.playlist_id
        WHERE TRY_TO_DATE(p.added_at) <= CURRENT_DATE()
        GROUP BY high_value.isrc, p.name, p.artist
    ),
    
    monthly_progression AS (
        SELECT 
            ps.isrc,
            ps.song_name,
            ps.artist,
            ps.first_playlist_date,
            l."Activity Year",
            l."Activity Month",
            l."Streams ATD" as cumulative_streams,
            ROW_NUMBER() OVER (
                PARTITION BY ps.isrc 
                ORDER BY l."Activity Year", l."Activity Month"
            ) as month_number
        FROM playlist_songs ps
        JOIN RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING l 
            ON ps.isrc = l.ISRC
        WHERE l.Territory = '{market_code}'
    ),
    
    hit_timing AS (
        SELECT 
            isrc,
            song_name,
            artist,
            first_playlist_date,
            MIN(CASE WHEN cumulative_streams >= 5000000 THEN month_number END) as months_to_5m,
            MAX(cumulative_streams) as final_total_streams
        FROM monthly_progression
        GROUP BY isrc, song_name, artist, first_playlist_date
        HAVING MAX(cumulative_streams) BETWEEN 5000000 AND 50000000
    )
    
    SELECT 
        CASE 
            WHEN months_to_5m <= 3 THEN '1-3 months to 5M'
            WHEN months_to_5m <= 6 THEN '4-6 months to 5M'
            WHEN months_to_5m <= 12 THEN '7-12 months to 5M'
            ELSE 'Over 1 year to 5M'
        END as time_to_5m,
        COUNT(*) as song_count,
        ROUND(COUNT(*) * 1.0 / SUM(COUNT(*)) OVER (), 3) as percentage,
        ROUND(AVG(final_total_streams/1000000), 1) as avg_final_streams_millions
    FROM hit_timing
    WHERE months_to_5m IS NOT NULL
    GROUP BY 
        CASE 
            WHEN months_to_5m <= 3 THEN '1-3 months to 5M'
            WHEN months_to_5m <= 6 THEN '4-6 months to 5M'
            WHEN months_to_5m <= 12 THEN '7-12 months to 5M'
            ELSE 'Over 1 year to 5M'
        END
    ORDER BY 
        CASE time_to_5m
            WHEN '1-3 months to 5M' THEN 1
            WHEN '4-6 months to 5M' THEN 2
            WHEN '7-12 months to 5M' THEN 3
            ELSE 4
        END;
    """


# ============================================================================
# QUERY 3: SEASONALITY - Best Release Months
# ============================================================================
def get_seasonality_query(market_code, genre):
    """
    Analyzes which months have highest hit rates
    
    Outputs:
    - playlist_month (1-12)
    - month_name (January, February, etc.)
    - songs_added
    - hit_rate_5_50m_percent
    """
    return f"""
    WITH hit_songs_5_50m AS (
        SELECT DISTINCT ISRC
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
        WHERE Territory = '{market_code}'
        GROUP BY ISRC
        HAVING MAX("Streams ATD") BETWEEN 5000000 AND 50000000
    )
    
    SELECT
        EXTRACT(MONTH FROM TRY_TO_DATE(p.added_at)) as playlist_month,
        MONTHNAME(TRY_TO_DATE(p.added_at)) as month_name,
        COUNT(*) as songs_added,
        ROUND(
            AVG(CASE WHEN hs.ISRC IS NOT NULL THEN 1 ELSE 0 END), 3
        ) as hit_rate_5_50m_percent
    FROM RIGHTSAPP_INSIGHTS.PUBLIC.SPOTIFY_PLAYLIST_DATA p
    INNER JOIN RIGHTSAPP_INSIGHTS.PUBLIC.SPOTHIGHVALUE_ISRCS h 
        ON p.isrc = h.isrc
    LEFT JOIN hit_songs_5_50m hs ON p.isrc = hs.ISRC
    WHERE TRY_TO_DATE(p.added_at) <= CURRENT_DATE()
    AND TRY_TO_DATE(p.added_at) IS NOT NULL
    GROUP BY 
        EXTRACT(MONTH FROM TRY_TO_DATE(p.added_at)), 
        MONTHNAME(TRY_TO_DATE(p.added_at))
    ORDER BY playlist_month;
    """


# ============================================================================
# QUERY 4: MOST COMMON PLAYLISTS - Volume analysis
# ============================================================================
def get_most_common_playlists_query(market_code, genre):
    """
    Lists playlists that appear most frequently in 5-50M hits
    
    Outputs:
    - playlist_name
    - hit_songs_count (how many 5-50M songs were on this playlist)
    - percentage_of_5_50m_hits
    - followers
    - activity_status
    """
    return f"""
    WITH hit_songs_5_50m AS (
        SELECT DISTINCT ISRC
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
        WHERE Territory = '{market_code}'
        GROUP BY ISRC
        HAVING MAX("Streams ATD") BETWEEN 5000000 AND 50000000
    ),
    
    playlist_hits AS (
        SELECT 
            h.playlist_name,
            COUNT(DISTINCT h.isrc) as hit_songs_count,
            ROUND(
                COUNT(DISTINCT h.isrc) * 1.0 / (SELECT COUNT(*) FROM hit_songs_5_50m), 3
            ) as percentage_of_5_50m_hits
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.SPOTHIGHVALUE_ISRCS h
        INNER JOIN hit_songs_5_50m hs ON h.isrc = hs.ISRC
        GROUP BY h.playlist_name
    ),
    
    playlist_activity AS (
        SELECT 
            playlist_name,
            MAX(TRY_TO_DATE(added_at)) as last_song_added,
            DATEDIFF('day', MAX(TRY_TO_DATE(added_at)), CURRENT_DATE()) as days_since_last_update,
            AVG(playlist_popularity) as avg_playlist_popularity
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.SPOTIFY_PLAYLIST_DATA
        WHERE TRY_TO_DATE(added_at) IS NOT NULL
        GROUP BY playlist_name
    )
    
    SELECT 
        ph.playlist_name,
        ph.hit_songs_count,
        ph.percentage_of_5_50m_hits,
        CONCAT(ROUND(pa.avg_playlist_popularity/1000000, 1), 'M') as followers,
        pa.last_song_added,
        pa.days_since_last_update,
        CASE 
            WHEN pa.days_since_last_update <= 7 THEN 'Very Active'
            WHEN pa.days_since_last_update <= 30 THEN 'Active'
            WHEN pa.days_since_last_update <= 90 THEN 'Moderate'
            WHEN pa.days_since_last_update <= 180 THEN 'Low Activity'
            ELSE 'Inactive'
        END as activity_status
    FROM playlist_hits ph
    LEFT JOIN playlist_activity pa ON ph.playlist_name = pa.playlist_name
    WHERE pa.last_song_added IS NOT NULL
    ORDER BY ph.hit_songs_count DESC
    LIMIT 30;
    """


# ============================================================================
# QUERY 5: SUMMARY STATISTICS
# ============================================================================
def get_summary_stats_query(market_code, genre):
    """
    Overall market summary statistics
    
    Outputs:
    - total_5_50m_songs
    - total_playlists
    - avg_playlists_per_song
    - avg_streams_millions
    - median_streams_millions
    """
    return f"""
    WITH hit_songs_5_50m AS (
        SELECT 
            ISRC,
            MAX("Streams ATD") as total_streams
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.LUMINATEMONTHLYSTREAMSBYRECORDING
        WHERE Territory = '{market_code}'
        GROUP BY ISRC
        HAVING MAX("Streams ATD") BETWEEN 5000000 AND 50000000
    ),
    
    playlist_counts AS (
        SELECT 
            p.isrc,
            COUNT(DISTINCT p.playlist_id) as playlist_count
        FROM RIGHTSAPP_INSIGHTS.PUBLIC.SPOTIFY_PLAYLIST_DATA p
        INNER JOIN hit_songs_5_50m hs ON p.isrc = hs.ISRC
        GROUP BY p.isrc
    )
    
    SELECT 
        COUNT(DISTINCT hs.ISRC) as total_5_50m_songs,
        COUNT(DISTINCT p.playlist_id) as total_playlists,
        ROUND(AVG(pc.playlist_count), 1) as avg_playlists_per_song,
        ROUND(AVG(hs.total_streams) / 1000000, 1) as avg_streams_millions,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY hs.total_streams) / 1000000, 1) as median_streams_millions
    FROM hit_songs_5_50m hs
    LEFT JOIN RIGHTSAPP_INSIGHTS.PUBLIC.SPOTIFY_PLAYLIST_DATA p ON hs.ISRC = p.isrc
    LEFT JOIN playlist_counts pc ON hs.ISRC = pc.isrc;
    """


# ============================================================================
# HELPER: Market code converter
# ============================================================================
def convert_market_to_code(market_name):
    """Convert market display name to territory code"""
    market_codes = {
        'France': 'FR',
        'Germany': 'DE',
        'Spain': 'ES',
        'UK': 'GB',
        'United Kingdom': 'GB',
        'US': 'US',
        'United States': 'US',
        'Thailand': 'TH',
        'Japan': 'JP',
        'Italy': 'IT',
        'Netherlands': 'NL',
        'Sweden': 'SE',
        'Norway': 'NO',
        'Brazil': 'BR',
        'Mexico': 'MX',
        'Australia': 'AU',
        'Canada': 'CA',
        'South Korea': 'KR',
        'Worldwide': 'WW'
    }
    return market_codes.get(market_name, market_name)