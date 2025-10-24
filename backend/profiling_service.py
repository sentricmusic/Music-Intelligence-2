"""
Profiling service for market/genre analysis using Snowflake
Orchestrates execution of all profiling queries
"""

import snowflake.connector
from profiling_queries import *
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class ProfilingService:
    """Service class for executing market/genre profiling queries"""
    
    def __init__(self, snowflake_conn=None):
        """Initialize with optional Snowflake connection"""
        self.conn = snowflake_conn
        self.logger = logging.getLogger(__name__)
        
    def _get_connection(self):
        """Get or create Snowflake connection"""
        if self.conn is None:
            try:
                self.conn = snowflake.connector.connect(
                    account=os.getenv('SNOWFLAKE_ACCOUNT'),
                    user=os.getenv('SNOWFLAKE_USER'),
                    password=os.getenv('SNOWFLAKE_PASSWORD'),
                    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
                    database=os.getenv('SNOWFLAKE_DATABASE', 'RIGHTSAPP_INSIGHTS'),
                    schema=os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
                )
            except Exception as e:
                self.logger.error(f"Failed to connect to Snowflake: {e}")
                return None
        return self.conn
    
    def _execute_query(self, query, query_name):
        """Execute SQL query and return results as list of dictionaries"""
        try:
            conn = self._get_connection()
            if conn is None:
                return []
                
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all results and convert to list of dicts
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            self.logger.info(f"✅ {query_name}: {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ {query_name} failed: {e}")
            return []
    
    def profile_market_genre(self, market_name, genre):
        """
        Run comprehensive profiling for a market/genre combination
        
        Args:
            market_name: Display name like 'France', 'UK', 'US'
            genre: Genre like 'Hip-Hop', 'Electronic', 'Pop'
            
        Returns:
            dict: Complete profiling results
        """
        # Convert market name to territory code
        market_code = convert_market_to_code(market_name)
        
        self.logger.info(f"🎯 Starting profiling: {market_name} ({market_code}) - {genre}")
        
        results = {
            'status': 'success',
            'market': market_code,
            'market_display': market_name,
            'genre': genre,
            'errors': []
        }
        
        try:
            # Execute all profiling queries
            
            # 1. Summary Statistics
            query = get_summary_stats_query(market_code, genre)
            summary_results = self._execute_query(query, "Summary Statistics")
            results['summary_stats'] = summary_results[0] if summary_results else {}
            
            # 2. Playlist Performance
            query = get_playlist_performance_query(market_code, genre)
            results['playlist_performance'] = self._execute_query(query, "Playlist Performance")
            
            # 3. Most Common Playlists
            query = get_most_common_playlists_query(market_code, genre)
            results['most_common_playlists'] = self._execute_query(query, "Most Common Playlists")
            
            # 4. Timing Analysis
            query = get_timing_analysis_query(market_code, genre)
            results['timing_analysis'] = self._execute_query(query, "Timing Analysis")
            
            # 5. Seasonality
            query = get_seasonality_query(market_code, genre)
            results['seasonality'] = self._execute_query(query, "Seasonality")
            
            # Check if we have any results
            total_results = sum([
                len(results.get('playlist_performance', [])),
                len(results.get('most_common_playlists', [])),
                len(results.get('timing_analysis', [])),
                len(results.get('seasonality', []))
            ])
            
            if total_results == 0:
                results['status'] = 'no_data'
                results['message'] = f'No profiling data found for {market_name} {genre}'
            else:
                self.logger.info(f"✅ Profiling completed: {total_results} total results")
            
        except Exception as e:
            self.logger.error(f"❌ Profiling failed: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            results['errors'].append(f"Profiling error: {e}")
        
        return results
    
    def get_market_insights(self, market_name, genre):
        """
        Get key insights summary for market/genre
        
        Returns:
            dict: Structured insights for reporting
        """
        profiling_data = self.profile_market_genre(market_name, genre)
        
        if profiling_data['status'] != 'success':
            return profiling_data
        
        insights = {
            'market': market_name,
            'genre': genre,
            'key_insights': []
        }
        
        try:
            # Extract top playlist
            if profiling_data.get('playlist_performance'):
                top_playlist = profiling_data['playlist_performance'][0]
                insights['key_insights'].append({
                    'type': 'top_playlist',
                    'title': f"Top Performing Playlist",
                    'description': f"{top_playlist['playlist_name']} has {top_playlist['hit_rate_5_50m_percent']*100:.1f}% hit rate",
                    'data': top_playlist
                })
            
            # Extract best month
            if profiling_data.get('seasonality'):
                best_month = max(profiling_data['seasonality'], key=lambda x: x['hit_rate_5_50m_percent'])
                insights['key_insights'].append({
                    'type': 'best_month',
                    'title': f"Peak Release Month",
                    'description': f"{best_month['month_name']} has {best_month['hit_rate_5_50m_percent']*100:.1f}% hit rate",
                    'data': best_month
                })
            
            # Extract market stats
            if profiling_data.get('summary_stats'):
                stats = profiling_data['summary_stats']
                insights['key_insights'].append({
                    'type': 'market_stats',
                    'title': f"Market Overview",
                    'description': f"{stats.get('total_5_50m_songs', 0)} songs reached 5-50M streams",
                    'data': stats
                })
            
        except Exception as e:
            insights['error'] = str(e)
        
        return insights
    
    def test_connection(self):
        """Test Snowflake connection and return status"""
        try:
            conn = self._get_connection()
            if conn is None:
                return {'status': 'error', 'message': 'Could not establish connection'}
            
            # Test with simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            
            return {
                'status': 'success', 
                'message': 'Snowflake connection successful',
                'database': os.getenv('SNOWFLAKE_DATABASE'),
                'schema': os.getenv('SNOWFLAKE_SCHEMA')
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'Connection failed: {e}'}


# Mock service for development/testing without Snowflake
class MockProfilingService(ProfilingService):
    """Mock profiling service that returns sample data"""
    
    def __init__(self):
        super().__init__(None)
    
    def profile_market_genre(self, market_name, genre):
        """Return mock profiling data"""
        market_code = convert_market_to_code(market_name)
        
        return {
            'status': 'success',
            'market': market_code,
            'market_display': market_name,
            'genre': genre,
            'summary_stats': {
                'total_5_50m_songs': 1250,
                'total_playlists': 145,
                'avg_playlists_per_song': 3.2,
                'avg_streams_millions': 12.8,
                'median_streams_millions': 8.5
            },
            'playlist_performance': [
                {
                    'playlist_name': f'Top {genre} {market_name}',
                    'total_songs': 524,
                    'songs_hit_5_50m': 127,
                    'hit_rate_5_50m_percent': 0.242,
                    'followers': '2.3M',
                    'activity_status': 'Very Active',
                    'ml_model_priority': 'High Priority'
                },
                {
                    'playlist_name': f'{genre} Hits {market_name}',
                    'total_songs': 312,
                    'songs_hit_5_50m': 58,
                    'hit_rate_5_50m_percent': 0.186,
                    'followers': '1.8M',
                    'activity_status': 'Active', 
                    'ml_model_priority': 'Medium Priority'
                }
            ],
            'most_common_playlists': [
                {'playlist_name': f'New Music Friday {market_name}', 'hit_songs_count': 89, 'percentage_of_5_50m_hits': 0.071},
                {'playlist_name': f'{genre} Central', 'hit_songs_count': 67, 'percentage_of_5_50m_hits': 0.054}
            ],
            'timing_analysis': [
                {'time_to_5m': '1-3 months to 5M', 'song_count': 312, 'percentage': 0.25, 'avg_final_streams_millions': 15.2},
                {'time_to_5m': '4-6 months to 5M', 'song_count': 487, 'percentage': 0.39, 'avg_final_streams_millions': 11.8},
                {'time_to_5m': '7-12 months to 5M', 'song_count': 298, 'percentage': 0.24, 'avg_final_streams_millions': 9.4},
                {'time_to_5m': 'Over 1 year to 5M', 'song_count': 153, 'percentage': 0.12, 'avg_final_streams_millions': 7.1}
            ],
            'seasonality': [
                {'playlist_month': 1, 'month_name': 'January', 'songs_added': 2341, 'hit_rate_5_50m_percent': 0.187},
                {'playlist_month': 2, 'month_name': 'February', 'songs_added': 2156, 'hit_rate_5_50m_percent': 0.201},
                {'playlist_month': 3, 'month_name': 'March', 'songs_added': 2487, 'hit_rate_5_50m_percent': 0.234},
                {'playlist_month': 4, 'month_name': 'April', 'songs_added': 2298, 'hit_rate_5_50m_percent': 0.198}
            ],
            'errors': []
        }
    
    def test_connection(self):
        return {'status': 'mock', 'message': 'Using mock data for development'}