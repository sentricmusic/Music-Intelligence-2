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
      const response = await fetch('http://localhost:5000/api/analyze', {
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
      
      const response = await fetch('http://localhost:5000/api/playlist-tracks', {
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
            </div>
          )}

        </div>
      </header>
    </div>
  );
}

export default App;