import React, { useState } from 'react';
import './App.css';
import logo from './sentric-logo.png';

function App() {
  const [market, setMarket] = useState('');
  const [genre, setGenre] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [isLoadingTracks, setIsLoadingTracks] = useState(false);
  const [tracks, setTracks] = useState(null);
  const [isLoadingCredits, setIsLoadingCredits] = useState(false);
  const [writerCredits, setWriterCredits] = useState(null);
  
  // Profiling states
  const [isProfilingLoading, setIsProfilingLoading] = useState(false);
  const [profilingData, setProfilingData] = useState(null);
  const [profilingError, setProfilingError] = useState(null);

  const markets = ['France', 'UK', 'Germany', 'Spain', 'US', 'Thailand', 'Japan'];
  const genres = ['Hip-Hop', 'Pop', 'Electronic', 'R&B', 'Rock'];

  const handleAnalyse = async () => {
    if (!market || !genre) {
      alert('Please select both market and genre');
      return;
    }
    
    setIsLoading(true);
    setResults(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ market, genre })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResults(data);
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      alert('Error connecting to backend: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFetchTracks = async () => {
    if (!results || !results.playlists) {
      alert('No playlists to fetch tracks from');
      return;
    }
    
    setIsLoadingTracks(true);
    setTracks(null);
    
    try {
      // Get playlist IDs from current results
      const playlistIds = results.playlists.map(p => p.playlist_id);
      
      const response = await fetch('http://localhost:5001/api/playlist-tracks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ playlist_ids: playlistIds })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setTracks(data);
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      alert('Error fetching tracks: ' + error.message);
    } finally {
      setIsLoadingTracks(false);
    }
  };

  const handleFetchWriterCredits = async () => {
    if (!tracks || !tracks.tracks) {
      alert('No tracks to fetch writer credits for');
      return;
    }
    
    setIsLoadingCredits(true);
    setWriterCredits(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/writer-credits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tracks: tracks.tracks })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setWriterCredits(data);
        
        // After writer credits are fetched, automatically start profiling
        handleProfileMarket();
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      alert('Error fetching writer credits: ' + error.message);
    } finally {
      setIsLoadingCredits(false);
    }
  };

  const handleProfileMarket = async () => {
    if (!market || !genre) {
      alert('Market and genre required for profiling');
      return;
    }
    
    setIsProfilingLoading(true);
    setProfilingData(null);
    setProfilingError(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ market, genre })
      });
      
      const data = await response.json();
      
      if (data.status === 'success' || data.status === 'mock') {
        setProfilingData(data);
      } else {
        setProfilingError(data.error || 'Profiling failed');
      }
    } catch (error) {
      setProfilingError('Error connecting to profiling service: ' + error.message);
    } finally {
      setIsProfilingLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} alt="Sentric Music" style={{ width: '250px', marginBottom: '20px' }} />
        <h1>Music Intelligence</h1>
        <p>Select market and genre to analyse</p>

        <div style={{ marginTop: '40px', width: tracks ? '90%' : '500px', maxWidth: tracks ? '1200px' : '500px' }}>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px', textAlign: 'left' }}>
              Market:
            </label>
            <select 
              value={market} 
              onChange={(e) => setMarket(e.target.value)}
              style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '8px', border: '2px solid #555' }}
            >
              <option value="">Select Market...</option>
              {markets.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px', textAlign: 'left' }}>
              Genre:
            </label>
            <select 
              value={genre} 
              onChange={(e) => setGenre(e.target.value)}
              style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '8px', border: '2px solid #555' }}
            >
              <option value="">Select Genre...</option>
              {genres.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
          </div>

          <button
            onClick={handleAnalyse}
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '16px',
              fontSize: '18px',
              fontWeight: 'bold',
              backgroundColor: isLoading ? '#ccc' : '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              marginTop: '20px'
            }}
          >
            {isLoading ? 'Analysing...' : 'Start Analyse'}
          </button>

          {/* RESULTS DISPLAY */}
          {results && (
            <div style={{
              marginTop: '40px',
              padding: '30px',
              backgroundColor: '#1e1e1e',
              borderRadius: '12px',
              border: '2px solid #4CAF50',
              textAlign: 'left'
            }}>
              <h2 style={{ color: '#4CAF50', marginTop: 0 }}>
                Results: {results.market} {results.genre}
              </h2>
              
              <p style={{ fontSize: '18px', marginBottom: '20px' }}>
                Found <strong>{results.playlists_found}</strong> playlists
              </p>

              <div style={{ marginTop: '20px' }}>
                <h3 style={{ color: '#fff', marginBottom: '15px' }}>Top Playlists:</h3>
                {results.playlists && results.playlists.length > 0 ? (
                  <div>
                    {results.playlists.map((playlist, idx) => (
                      <div 
                        key={idx}
                        style={{
                          backgroundColor: '#2d2d2d',
                          padding: '15px',
                          marginBottom: '10px',
                          borderRadius: '8px',
                          border: '1px solid #444'
                        }}
                      >
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#fff', marginBottom: '5px' }}>
                          {idx + 1}. {playlist.playlist_name}
                        </div>
                        <div style={{ fontSize: '14px', color: '#aaa' }}>
                          Owner: {playlist.owner} | Saves: {playlist.followers.toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: '#999' }}>No playlists found</p>
                )}
              </div>

              {/* FETCH TRACKS BUTTON */}
              <button
                onClick={handleFetchTracks}
                disabled={isLoadingTracks}
                style={{
                  width: '100%',
                  padding: '16px',
                  fontSize: '18px',
                  fontWeight: 'bold',
                  backgroundColor: isLoadingTracks ? '#ccc' : '#2196F3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isLoadingTracks ? 'not-allowed' : 'pointer',
                  marginTop: '20px'
                }}
              >
                {isLoadingTracks ? 'Fetching Track Details...' : 'Fetch Track Details'}
              </button>
            </div>
          )}

          {/* TRACKS DISPLAY */}
          {tracks && (
            <div style={{
              marginTop: '40px',
              padding: '30px',
              backgroundColor: '#1a1a1a',
              borderRadius: '12px',
              border: '2px solid #2196F3',
              textAlign: 'left',
              maxHeight: '700px',
              overflowY: 'auto',
              width: '100%'
            }}>
              <h2 style={{ color: '#2196F3', marginTop: 0 }}>
                Track Details
              </h2>
              
              <p style={{ fontSize: '18px', marginBottom: '20px', color: '#fff' }}>
                Found <strong>{tracks.total_tracks}</strong> tracks across {results.playlists.length} playlists
              </p>

              <div style={{ marginTop: '20px' }}>
                {tracks.tracks && tracks.tracks.length > 0 ? (
                  <div>
                    {tracks.tracks.slice(0, 50).map((track, idx) => (
                      <div 
                        key={idx}
                        style={{
                          backgroundColor: '#2a2a2a',
                          padding: '16px',
                          marginBottom: '10px',
                          borderRadius: '8px',
                          border: '1px solid #333',
                          display: 'grid',
                          gridTemplateColumns: '2fr 1fr',
                          gap: '20px',
                          alignItems: 'start'
                        }}
                      >
                        <div>
                          <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#fff', marginBottom: '6px' }}>
                            {track.track_name} - {track.track_artist}
                          </div>
                          <div style={{ fontSize: '13px', color: '#aaa', marginBottom: '6px' }}>
                            Playlist: {track.playlist_name} ({track.playlist_followers?.toLocaleString()} saves)
                          </div>
                        </div>
                        <div style={{ fontSize: '13px', color: '#888', textAlign: 'right' }}>
                          <div>Added: {track.track_added_at?.substring(0, 10)}</div>
                          <div>Released: {track.track_release_date}</div>
                          <div>Popularity: {track.track_popularity}</div>
                          <div>ISRC: {track.isrc || 'N/A'}</div>
                        </div>
                      </div>
                    ))}
                    {tracks.tracks.length > 50 && (
                      <p style={{ color: '#888', textAlign: 'center', marginTop: '20px' }}>
                        Showing first 50 of {tracks.total_tracks} tracks...
                      </p>
                    )}
                  </div>
                ) : (
                  <p style={{ color: '#999' }}>No tracks found</p>
                )}
              </div>

              {/* WRITER CREDITS BUTTON */}
              <button
                onClick={handleFetchWriterCredits}
                disabled={isLoadingCredits}
                style={{
                  width: '100%',
                  padding: '16px',
                  fontSize: '18px',
                  fontWeight: 'bold',
                  backgroundColor: isLoadingCredits ? '#ccc' : '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isLoadingCredits ? 'not-allowed' : 'pointer',
                  marginTop: '20px'
                }}
              >
                {isLoadingCredits ? 'Fetching Writer Credits from Apple Music...' : 'Get Writer Credits (Apple Music)'}
              </button>
            </div>
          )}

          {/* WRITER CREDITS DISPLAY */}
          {writerCredits && (
            <div style={{
              marginTop: '40px',
              padding: '30px',
              backgroundColor: '#1a1a1a',
              borderRadius: '12px',
              border: '2px solid #4CAF50',
              textAlign: 'left',
              maxHeight: '700px',
              overflowY: 'auto',
              width: '100%'
            }}>
              <h2 style={{ color: '#4CAF50', marginTop: 0 }}>
                Writer Credits (Apple Music)
              </h2>
              
              {/* Stats Summary */}
              <div style={{
                backgroundColor: '#2a2a2a',
                padding: '20px',
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #333'
              }}>
                <h3 style={{ color: '#4CAF50', marginTop: 0, marginBottom: '15px' }}>
                  Processing Results
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                  <div style={{ color: '#fff' }}>
                    <strong>Total Processed:</strong> {writerCredits.stats.total_processed}
                  </div>
                  <div style={{ color: '#fff' }}>
                    <strong>Has ISRC:</strong> {writerCredits.stats.has_isrc}
                  </div>
                  <div style={{ color: '#fff' }}>
                    <strong>Found in Apple Music:</strong> {writerCredits.stats.found_in_apple_music}
                  </div>
                  <div style={{ color: '#fff' }}>
                    <strong>Has Writer Credits:</strong> {writerCredits.stats.has_writer_credits}
                  </div>
                  <div style={{ color: '#4CAF50' }}>
                    <strong>Apple Music Success Rate:</strong> {writerCredits.stats.apple_music_success_rate}
                  </div>
                  <div style={{ color: '#4CAF50' }}>
                    <strong>Writer Credits Rate:</strong> {writerCredits.stats.writer_credits_rate}
                  </div>
                  <div style={{ color: '#FFD700' }}>
                    <strong>Total IPIs Found:</strong> {writerCredits.tracks.reduce((total, track) => total + (track.total_ipis_found || 0), 0)}
                  </div>
                  <div style={{ color: '#E91E63' }}>
                    <strong>Artist IPIs Found:</strong> {writerCredits.tracks.filter(track => track.main_artist_ipi).length}
                  </div>
                </div>
              </div>

              {/* Track Details with Writer Credits */}
              <div style={{ marginTop: '20px' }}>
                {writerCredits.tracks && writerCredits.tracks.length > 0 ? (
                  <div>
                    {writerCredits.tracks.slice(0, 50).map((track, idx) => (
                      <div 
                        key={idx}
                        style={{
                          backgroundColor: '#2a2a2a',
                          padding: '16px',
                          marginBottom: '10px',
                          borderRadius: '8px',
                          border: track.composer_names ? '1px solid #4CAF50' : '1px solid #333'
                        }}
                      >
                        <div style={{
                          display: 'grid',
                          gridTemplateColumns: '2fr 1fr',
                          gap: '20px',
                          alignItems: 'start'
                        }}>
                          <div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#fff', marginBottom: '6px' }}>
                              {track.track_name} - {track.track_artist}
                            </div>
                            <div style={{ fontSize: '13px', color: '#aaa', marginBottom: '6px' }}>
                              Playlist: {track.playlist_name}
                            </div>
                            {/* Writer Credits */}
                            {track.composer_names ? (
                              <div style={{ 
                                fontSize: '14px', 
                                color: '#4CAF50', 
                                marginTop: '10px',
                                padding: '10px',
                                backgroundColor: '#1e3d1e',
                                borderRadius: '4px',
                                border: '1px solid #4CAF50'
                              }}>
                                <strong>Writers:</strong> {track.composer_names}
                                <div style={{ fontSize: '12px', color: '#aaa', marginTop: '4px' }}>
                                  ({track.composer_count} writer{track.composer_count !== 1 ? 's' : ''})
                                </div>
                                
                                {/* IPI Numbers Display */}
                                {track.main_artist_ipi && (
                                  <div style={{ fontSize: '12px', color: '#FFD700', marginTop: '6px' }}>
                                    🎤 Main Artist IPI: {track.main_artist_ipi}
                                  </div>
                                )}
                                
                                {track.writer_ipis && track.writer_ipis.length > 0 && (
                                  <div style={{ fontSize: '12px', color: '#FFD700', marginTop: '6px' }}>
                                    ✍️ Writer IPIs:
                                    {track.writer_ipis.map((writer, idx) => (
                                      <div key={idx} style={{ marginLeft: '10px', marginTop: '2px' }}>
                                        • {writer.name} → {writer.ipi}
                                      </div>
                                    ))}
                                  </div>
                                )}
                                
                                {track.total_ipis_found > 0 && (
                                  <div style={{ fontSize: '12px', color: '#90EE90', marginTop: '6px', fontWeight: 'bold' }}>
                                    📊 Total IPIs Found: {track.total_ipis_found}
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div style={{ 
                                fontSize: '13px', 
                                color: '#888', 
                                marginTop: '10px',
                                fontStyle: 'italic'
                              }}>
                                {track.api_status === 'no_isrc' ? 'No ISRC available' : 
                                 track.api_status === 'not_found' ? 'Not found in Apple Music' :
                                 track.api_status === 'error' ? 'Apple Music API error' :
                                 'No writer credits available'}
                              </div>
                            )}
                          </div>
                          <div style={{ fontSize: '13px', color: '#888', textAlign: 'right' }}>
                            <div>ISRC: {track.isrc || 'N/A'}</div>
                            <div>Apple Music: {track.api_status}</div>
                            <div>Popularity: {track.track_popularity}</div>
                            <div>Released: {track.track_release_date}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                    {writerCredits.tracks.length > 50 && (
                      <p style={{ color: '#888', textAlign: 'center', marginTop: '20px' }}>
                        Showing first 50 of {writerCredits.stats.total_processed} tracks...
                      </p>
                    )}
                  </div>
                ) : (
                  <p style={{ color: '#999' }}>No writer credits found</p>
                )}
              </div>
            </div>
          )}

          {/* Profiling Loading State */}
          {isProfilingLoading && (
            <div style={{ 
              textAlign: 'center', 
              marginTop: '30px', 
              padding: '20px',
              backgroundColor: '#2a2a2a',
              borderRadius: '10px'
            }}>
              <div style={{ color: '#4CAF50', fontSize: '18px', marginBottom: '10px' }}>
                📊 Profiling market data for {market} {genre}...
              </div>
              <div style={{ color: '#fff' }}>
                Analyzing historical 5-50M hits, playlist performance, and market insights
              </div>
            </div>
          )}

          {/* Profiling Error */}
          {profilingError && (
            <div style={{ 
              textAlign: 'center', 
              marginTop: '30px', 
              padding: '20px',
              backgroundColor: '#3a1a1a',
              borderRadius: '10px',
              border: '1px solid #ff4444'
            }}>
              <div style={{ color: '#ff4444', fontSize: '16px' }}>
                ❌ Profiling Error: {profilingError}
              </div>
            </div>
          )}

          {/* Profiling Results */}
          {profilingData && profilingData.status === 'success' && (
            <div style={{ 
              marginTop: '30px', 
              padding: '20px',
              backgroundColor: '#2a2a2a',
              borderRadius: '10px',
              border: '2px solid #4CAF50'
            }}>
              <h2 style={{ color: '#4CAF50', textAlign: 'center', marginBottom: '20px' }}>
                📊 Market Profile: {profilingData.market_display} {profilingData.genre}
              </h2>
              
              {/* Summary Stats */}
              {profilingData.summary_stats && (
                <div style={{ marginBottom: '30px' }}>
                  <h3 style={{ color: '#fff', marginBottom: '15px' }}>📈 Market Overview</h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                    gap: '15px' 
                  }}>
                    <div style={{ backgroundColor: '#1a3d1a', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
                      <div style={{ color: '#4CAF50', fontSize: '24px', fontWeight: 'bold' }}>
                        {profilingData.summary_stats.total_5_50m_songs || 0}
                      </div>
                      <div style={{ color: '#aaa', fontSize: '14px' }}>Total 5-50M Hits</div>
                    </div>
                    <div style={{ backgroundColor: '#1a3d1a', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
                      <div style={{ color: '#4CAF50', fontSize: '24px', fontWeight: 'bold' }}>
                        {profilingData.summary_stats.total_playlists || 0}
                      </div>
                      <div style={{ color: '#aaa', fontSize: '14px' }}>Total Playlists</div>
                    </div>
                    <div style={{ backgroundColor: '#1a3d1a', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
                      <div style={{ color: '#4CAF50', fontSize: '24px', fontWeight: 'bold' }}>
                        {profilingData.summary_stats.avg_streams_millions || 0}M
                      </div>
                      <div style={{ color: '#aaa', fontSize: '14px' }}>Avg Streams</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Top Playlists */}
              {profilingData.playlist_performance && profilingData.playlist_performance.length > 0 && (
                <div style={{ marginBottom: '30px' }}>
                  <h3 style={{ color: '#fff', marginBottom: '15px' }}>🎵 Top Performing Playlists</h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#1a1a1a' }}>
                          <th style={{ color: '#4CAF50', padding: '12px', textAlign: 'left', borderBottom: '2px solid #4CAF50' }}>Playlist</th>
                          <th style={{ color: '#4CAF50', padding: '12px', textAlign: 'center', borderBottom: '2px solid #4CAF50' }}>Hit Rate</th>
                          <th style={{ color: '#4CAF50', padding: '12px', textAlign: 'center', borderBottom: '2px solid #4CAF50' }}>Hit Songs</th>
                          <th style={{ color: '#4CAF50', padding: '12px', textAlign: 'center', borderBottom: '2px solid #4CAF50' }}>Activity</th>
                          <th style={{ color: '#4CAF50', padding: '12px', textAlign: 'center', borderBottom: '2px solid #4CAF50' }}>Priority</th>
                        </tr>
                      </thead>
                      <tbody>
                        {profilingData.playlist_performance.slice(0, 10).map((playlist, idx) => (
                          <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? '#2a2a2a' : '#333' }}>
                            <td style={{ color: '#fff', padding: '12px', maxWidth: '200px' }}>
                              {playlist.playlist_name}
                            </td>
                            <td style={{ color: '#4CAF50', padding: '12px', textAlign: 'center', fontWeight: 'bold' }}>
                              {(playlist.hit_rate_5_50m_percent * 100).toFixed(1)}%
                            </td>
                            <td style={{ color: '#fff', padding: '12px', textAlign: 'center' }}>
                              {playlist.songs_hit_5_50m}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>
                              <span style={{
                                padding: '4px 8px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                backgroundColor: playlist.activity_status === 'Very Active' ? '#4CAF50' : 
                                                playlist.activity_status === 'Active' ? '#2196F3' : 
                                                playlist.activity_status === 'Moderate' ? '#FF9800' : '#f44336',
                                color: '#fff'
                              }}>
                                {playlist.activity_status}
                              </span>
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>
                              <span style={{
                                padding: '4px 8px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                backgroundColor: playlist.ml_model_priority === 'High Priority' ? '#4CAF50' : 
                                                playlist.ml_model_priority === 'Medium Priority' ? '#FF9800' : '#666',
                                color: '#fff'
                              }}>
                                {playlist.ml_model_priority}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Timing Analysis */}
              {profilingData.timing_analysis && profilingData.timing_analysis.length > 0 && (
                <div style={{ marginBottom: '30px' }}>
                  <h3 style={{ color: '#fff', marginBottom: '15px' }}>⏱️ Time to Success (5M Streams)</h3>
                  {profilingData.timing_analysis.map((timing, idx) => (
                    <div key={idx} style={{ 
                      marginBottom: '10px', 
                      display: 'flex', 
                      alignItems: 'center',
                      backgroundColor: '#1a1a1a',
                      padding: '12px',
                      borderRadius: '8px'
                    }}>
                      <div style={{ color: '#fff', width: '150px', fontSize: '14px' }}>
                        {timing.time_to_5m}
                      </div>
                      <div style={{ 
                        flex: 1, 
                        backgroundColor: '#333', 
                        height: '20px', 
                        borderRadius: '10px', 
                        position: 'relative',
                        marginRight: '15px'
                      }}>
                        <div style={{ 
                          backgroundColor: '#4CAF50', 
                          height: '100%', 
                          width: `${timing.percentage * 100}%`, 
                          borderRadius: '10px',
                          minWidth: '2px'
                        }} />
                      </div>
                      <div style={{ color: '#4CAF50', fontWeight: 'bold', width: '60px', textAlign: 'right' }}>
                        {(timing.percentage * 100).toFixed(1)}%
                      </div>
                      <div style={{ color: '#aaa', width: '100px', textAlign: 'right', fontSize: '12px' }}>
                        {timing.song_count} songs
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {profilingData.status === 'mock' && (
                <div style={{ 
                  textAlign: 'center', 
                  color: '#FFD700', 
                  fontSize: '14px',
                  marginTop: '20px',
                  padding: '10px',
                  backgroundColor: '#3d3d1a',
                  borderRadius: '8px'
                }}>
                  ⚠️ Currently showing mock data. Connect Snowflake for real market analysis.
                </div>
              )}
            </div>
          )}

        </div>
      </header>
    </div>
  );
}

export default App;