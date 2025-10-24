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
        """Return REVOLUTIONARY music intelligence mock data with baseline vs incremental analysis"""
        market_code = convert_market_to_code(market_name)
        
        return {
            'status': 'success',
            'market': market_code,
            'market_display': market_name,
            'genre': genre,
            
            # KEY INNOVATION: Summary with baseline vs incremental analysis
            'summary_stats': {
                'total_5_50m_hits': 347,  # Songs that actually hit 5-50M from playlists
                'total_playlist_songs_analyzed': 1243,  # Total songs pulled from playlists
                'playlist_driven_hits': 347,  # Songs where playlists drove success (vs already popular)
                'avg_baseline_when_playlisted': 0.42,  # 420K avg streams when first added
                'avg_final_streams': 16.8,  # 16.8M final average
                'avg_incremental_from_playlists': 16.4,  # 16.4M driven by playlists (proof!)
                'median_time_to_5m_months': 4.3,
                'avg_playlists_per_hit': 7.2,
                'gateway_success_rate': 0.73  # 73% of songs reaching gateway in 14 days succeed
            },
            
            # TIER-BASED PLAYLIST ANALYSIS (with real impact data)
            'playlist_tiers': [
                {
                    'tier': 'Tier 1 - Editorial Flagships',
                    'playlists': [
                        {
                            'playlist_name': f'Radar {market_name}' if market_name != 'US' else 'RapCaviar',
                            'tier': 1,
                            'playlist_type': 'Editorial Gateway',
                            'followers': '3.2M',
                            'songs_analyzed': 241,
                            'hits_produced': 167,
                            'hit_rate': 0.69,  # 69% - incredible!
                            'avg_incremental_streams': 22.5,  # 22.5M avg boost
                            'avg_baseline_when_added': 0.38,  # Songs added early (380K baseline)
                            'activity_status': 'Very Active',
                            'adds_per_week': 12,
                            'is_gateway': True,
                            'gateway_to_mainstream_rate': 0.84  # 84% go mainstream after this
                        },
                        {
                            'playlist_name': f'New Music Friday {market_name}',
                            'tier': 1,
                            'playlist_type': 'Editorial Spotlight',
                            'followers': '4.8M',
                            'songs_analyzed': 198,
                            'hits_produced': 89,
                            'hit_rate': 0.45,  # 45% hit rate
                            'avg_incremental_streams': 18.7,
                            'avg_baseline_when_added': 0.85,  # Added later (850K baseline)
                            'activity_status': 'Very Active',
                            'adds_per_week': 8,
                            'is_gateway': True,
                            'gateway_to_mainstream_rate': 0.91
                        }
                    ]
                },
                {
                    'tier': 'Tier 2 - Genre Leaders',
                    'playlists': [
                        {
                            'playlist_name': f'Générations {genre} {market_code}' if market_name == 'France' else f'{genre} Central',
                            'tier': 2,
                            'playlist_type': 'Genre Authority',
                            'followers': '1.9M',
                            'songs_analyzed': 156,
                            'hits_produced': 67,
                            'hit_rate': 0.43,  # 43% hit rate
                            'avg_incremental_streams': 12.3,
                            'avg_baseline_when_added': 0.52,
                            'activity_status': 'Active',
                            'adds_per_week': 6,
                            'is_gateway': False,
                            'gateway_to_mainstream_rate': 0.31
                        },
                        {
                            'playlist_name': f'{genre} Workout',
                            'tier': 2,
                            'playlist_type': 'Context Curator',
                            'followers': '2.1M',
                            'songs_analyzed': 134,
                            'hits_produced': 41,
                            'hit_rate': 0.31,
                            'avg_incremental_streams': 8.9,
                            'avg_baseline_when_added': 0.71,
                            'activity_status': 'Active',
                            'adds_per_week': 4,
                            'is_gateway': False,
                            'gateway_to_mainstream_rate': 0.22
                        }
                    ]
                },
                {
                    'tier': 'Tier 3 - Discovery Engines',
                    'playlists': [
                        {
                            'playlist_name': 'POLLEN' if market_name == 'France' else 'Fresh Finds',
                            'tier': 3,
                            'playlist_type': 'Discovery/Emerging',
                            'followers': '680K',
                            'songs_analyzed': 298,
                            'hits_produced': 56,
                            'hit_rate': 0.19,
                            'avg_incremental_streams': 4.2,
                            'avg_baseline_when_added': 0.15,  # Very early (150K baseline)
                            'activity_status': 'Very Active',
                            'adds_per_week': 15,
                            'is_gateway': False,
                            'gateway_to_mainstream_rate': 0.68  # Good stepping stone
                        }
                    ]
                }
            ],
            
            # GATEWAY DETECTION - The magic crossover analysis
            'gateway_analysis': {
                'primary_gateways': [
                    {
                        'playlist_name': f'Radar {market_name}' if market_name != 'US' else 'RapCaviar',
                        'gateway_type': 'Genre → Mainstream Bridge',
                        'songs_that_crossed_over': 167,
                        'crossover_success_rate': 0.84,
                        'avg_days_to_mainstream': 14,
                        'next_playlists': [
                            {'playlist': f'Top {market_name}', 'frequency': 89, 'avg_days': 21},
                            {'playlist': f'Viral 50 {market_name}', 'frequency': 67, 'avg_days': 18},
                            {'playlist': f'New Music Friday {market_name}', 'frequency': 45, 'avg_days': 12}
                        ]
                    }
                ],
                'gateway_timing': {
                    'fast_track_14_days': {'songs': 127, 'success_rate': 0.73},
                    'normal_15_30_days': {'songs': 89, 'success_rate': 0.41},
                    'slow_31_60_days': {'songs': 34, 'success_rate': 0.26},
                    'very_slow_60_plus': {'songs': 18, 'success_rate': 0.11}
                }
            },
            
            # PLAYLIST JOURNEY PATHS - Common sequences to success
            'journey_paths': [
                {
                    'path_name': 'Discovery → Gateway → Mainstream',
                    'sequence': f'POLLEN → Radar {market_name} → Top {market_name}',
                    'frequency': 87,
                    'success_rate': 0.89,
                    'avg_timeline_days': 45,
                    'step_1': {'playlist': 'POLLEN', 'avg_baseline': 0.15, 'avg_days_to_next': 14},
                    'step_2': {'playlist': f'Radar {market_name}', 'avg_baseline': 0.58, 'avg_days_to_next': 21},
                    'step_3': {'playlist': f'Top {market_name}', 'avg_baseline': 3.2, 'avg_days_to_next': None},
                    'avg_final_streams': 22.1
                },
                {
                    'path_name': 'Genre Leader → Editorial → Viral',
                    'sequence': f'Générations {genre} → New Music Friday {market_name} → Viral 50 {market_name}',
                    'frequency': 62,
                    'success_rate': 0.76,
                    'avg_timeline_days': 31,
                    'step_1': {'playlist': f'Générations {genre}', 'avg_baseline': 0.31, 'avg_days_to_next': 8},
                    'step_2': {'playlist': f'New Music Friday {market_name}', 'avg_baseline': 1.1, 'avg_days_to_next': 18},
                    'step_3': {'playlist': f'Viral 50 {market_name}', 'avg_baseline': 4.8, 'avg_days_to_next': None},
                    'avg_final_streams': 15.3
                },
                {
                    'path_name': 'Failed Path (Stalled)',
                    'sequence': f'{genre} Workout → Chill {genre} → [STALLED]',
                    'frequency': 34,
                    'success_rate': 0.12,
                    'avg_timeline_days': 120,
                    'step_1': {'playlist': f'{genre} Workout', 'avg_baseline': 0.09, 'avg_days_to_next': 45},
                    'step_2': {'playlist': f'Chill {genre}', 'avg_baseline': 0.31, 'avg_days_to_next': None},
                    'step_3': {'playlist': 'NEVER REACHED MAINSTREAM', 'avg_baseline': None, 'avg_days_to_next': None},
                    'avg_final_streams': 2.1
                }
            ],
            
            # PLAYLIST VELOCITY ANALYSIS - Speed is everything!
            'velocity_analysis': {
                'summary': {
                    'total_songs_analyzed': 445,
                    'velocity_correlation': 'STRONG POSITIVE - Faster playlist adoption = Higher hit rate',
                    'key_insight': 'Multiple playlists picking up a song QUICKLY = strongest success predictor'
                },
                'velocity_tiers': [
                    {
                        'velocity_type': 'Lightning Fast',
                        'definition': '6+ playlists in first 30 days',
                        'songs_count': 89,
                        'hits_produced': 42,
                        'hit_rate': 0.47,  # 47% - INCREDIBLE!
                        'avg_incremental_streams': 18.2,
                        'avg_baseline_at_first_playlist': 0.31,  # Early adoption
                        'avg_days_to_first_playlist': 3,
                        'avg_days_to_6th_playlist': 22,
                        'typical_sequence': 'Discovery → 3 Genre → 2 Gateway → Mainstream',
                        'success_indicator': 'HIGHEST - Strong industry consensus'
                    },
                    {
                        'velocity_type': 'Fast',
                        'definition': '3-5 playlists in first 30 days', 
                        'songs_count': 134,
                        'hits_produced': 67,
                        'hit_rate': 0.50,  # 50% - Even better rate!
                        'avg_incremental_streams': 14.7,
                        'avg_baseline_at_first_playlist': 0.28,
                        'avg_days_to_first_playlist': 5,
                        'avg_days_to_5th_playlist': 26,
                        'typical_sequence': 'Discovery → Gateway → Mainstream',
                        'success_indicator': 'HIGH - Good momentum'
                    },
                    {
                        'velocity_type': 'Moderate',
                        'definition': '2-3 playlists in first 60 days',
                        'songs_count': 98, 
                        'hits_produced': 31,
                        'hit_rate': 0.32,  # 32% - Okay but concerning
                        'avg_incremental_streams': 8.9,
                        'avg_baseline_at_first_playlist': 0.45,
                        'avg_days_to_first_playlist': 12,
                        'avg_days_to_3rd_playlist': 48,
                        'typical_sequence': 'Genre → Gateway → Maybe Mainstream',
                        'success_indicator': 'MEDIUM - Lukewarm industry response'
                    },
                    {
                        'velocity_type': 'Slow',
                        'definition': '1-2 playlists in first 90 days',
                        'songs_count': 124,
                        'hits_produced': 15, 
                        'hit_rate': 0.12,  # 12% - DANGER ZONE
                        'avg_incremental_streams': 3.4,
                        'avg_baseline_at_first_playlist': 0.67,  # Already had traction
                        'avg_days_to_first_playlist': 21,
                        'avg_days_to_2nd_playlist': 67,
                        'typical_sequence': 'Single genre playlist → Stalled',
                        'success_indicator': 'LOW - Weak industry interest'
                    }
                ],
                'velocity_insights': [
                    {
                        'insight': 'The 30-day window is CRITICAL',
                        'data': 'Songs with 3+ playlists in 30 days = 48% avg hit rate vs 12% for slow songs'
                    },
                    {
                        'insight': 'Early adoption matters more than baseline streams',
                        'data': 'Fast songs start at 0.28-0.31M baseline, slow songs at 0.67M but fail'
                    },
                    {
                        'insight': 'Industry consensus is the strongest predictor', 
                        'data': 'Multiple curators choosing the same song independently = gold'
                    }
                ]
            },
            
            # WRITER SUCCESS INTELLIGENCE - Publishing gold!
            'writer_success': [
                {
                    'writer_name': 'Pierre Dubois',
                    'total_tracks_analyzed': 18,
                    'hits_produced': 11,
                    'hit_rate': 0.61,  # 61% vs 23% market average!
                    'market_average_hit_rate': 0.23,
                    'performance_multiplier': 2.7,  # 2.7x better than average
                    'avg_streams_per_track': 19.2,
                    'avg_baseline_when_discovered': 0.18,  # Catches songs early
                    'avg_incremental_contribution': 18.8,
                    'typical_journey': 'Discovery → Gateway → Mainstream (Fast)',
                    'avg_time_to_5m': 3.1,
                    'writer_status': 'PRIORITY WRITER'
                },
                {
                    'writer_name': 'Marie Laurent',
                    'total_tracks_analyzed': 22,
                    'hits_produced': 4,
                    'hit_rate': 0.18,  # Below average
                    'market_average_hit_rate': 0.23,
                    'performance_multiplier': 0.8,
                    'avg_streams_per_track': 7.1,
                    'avg_baseline_when_discovered': 1.2,  # Songs already had traction
                    'avg_incremental_contribution': 5.8,
                    'typical_journey': 'Mid-level entry → Inconsistent',
                    'avg_time_to_5m': 8.2,
                    'writer_status': 'BELOW AVERAGE'
                },
                {
                    'writer_name': 'Alex Chen',
                    'total_tracks_analyzed': 15,
                    'hits_produced': 8,
                    'hit_rate': 0.53,  # Above average
                    'market_average_hit_rate': 0.23,
                    'performance_multiplier': 2.3,
                    'avg_streams_per_track': 16.4,
                    'avg_baseline_when_discovered': 0.21,
                    'avg_incremental_contribution': 16.1,
                    'typical_journey': 'Discovery → Gateway → Mainstream (Consistent)',
                    'avg_time_to_5m': 3.8,
                    'writer_status': 'HIGH VALUE'
                }
            ],
            
            # SEASONALITY with actual impact
            'seasonality': [
                {'month': 1, 'month_name': 'January', 'songs_added': 134, 'hit_rate': 0.18, 'avg_incremental': 12.4},
                {'month': 2, 'month_name': 'February', 'songs_added': 121, 'hit_rate': 0.14, 'avg_incremental': 10.1},
                {'month': 3, 'month_name': 'March', 'songs_added': 156, 'hit_rate': 0.31, 'avg_incremental': 18.9},  # Best!
                {'month': 9, 'month_name': 'September', 'songs_added': 142, 'hit_rate': 0.31, 'avg_incremental': 17.2},  # Also great
                {'month': 10, 'month_name': 'October', 'songs_added': 138, 'hit_rate': 0.26, 'avg_incremental': 15.8},
                {'month': 12, 'month_name': 'December', 'songs_added': 98, 'hit_rate': 0.12, 'avg_incremental': 7.9}   # Worst
            ],
            
            'errors': []
        }
    
    def test_connection(self):
        return {'status': 'mock', 'message': 'Using mock data for development'}