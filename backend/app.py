from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return res.json()["access_token"]

def search_playlists(market, genre, token):
    # Convert full country names to ISO codes for Spotify API
    market_codes = {
        'France': 'FR',
        'UK': 'GB',
        'Germany': 'DE',
        'Spain': 'ES',
        'US': 'US',
        'Thailand': 'TH',
        'Japan': 'JP'
    }
    
    market_code = market_codes.get(market, market)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": f"{market} {genre}",
        "type": "playlist",
        "market": market_code,  # Use code here
        "limit": 20
    }
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    data = response.json()
    items = data.get("playlists", {}).get("items", [])
    
    playlists = []
    for item in items:
        if not item:
            continue
        playlists.append({
            "playlist_name": item.get("name"),
            "playlist_id": item.get("id"),
            "owner": item.get("owner", {}).get("display_name", "Unknown"),
            "followers": item.get("followers", {}).get("total", 0)
        })
    
    return playlists

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    market = data.get('market')
    genre = data.get('genre')
    
    if not market or not genre:
        return jsonify({'error': 'Market and genre required'}), 400
    
    try:
        token = get_spotify_token()
        playlists = search_playlists(market, genre, token)
        
        return jsonify({
            'success': True,
            'market': market,
            'genre': genre,
            'playlists_found': len(playlists),
            'playlists': playlists[:5]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)