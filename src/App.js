import React, { useState } from 'react';
import './App.css';
import logo from './sentric-logo.png';

function App() {
  const [market, setMarket] = useState('');
  const [genre, setGenre] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const markets = ['France', 'UK', 'Germany', 'Spain', 'US', 'Thailand', 'Japan'];
  const genres = ['Hip-Hop', 'Pop', 'Electronic', 'R&B', 'Rock'];

  const handleAnalyse = () => {
    if (!market || !genre) {
      alert('Please select both market and genre');
      return;
    }
    setIsLoading(true);
    console.log(`Analysing ${market} ${genre}...`);
    // Later we'll connect to Python backend here
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} alt="Sentric Music" style={{ width: '250px', marginBottom: '20px' }} />
        <h1>Music Intelligence</h1>
        <p>Select market and genre to analyse</p>

        <div style={{ marginTop: '40px', width: '400px' }}>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px', textAlign: 'left' }}>
              Market:
            </label>
            <select 
              value={market} 
              onChange={(e) => setMarket(e.target.value)}
              style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '8px' }}
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
              style={{ width: '100%', padding: '12px', fontSize: '16px', borderRadius: '8px' }}
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

        </div>
      </header>
    </div>
  );
}

export default App;
