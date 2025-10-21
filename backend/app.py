from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os
import time
import jwt
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Apple Music API credentials
APPLE_TEAM_ID = "2MQ6NB4Q3C"
APPLE_KEY_ID = "FH2F6F277R"
APPLE_PRIVATE_KEY_PATH = r"c:\Users\kaz.roche\Downloads\AuthKey_FH2F6F277R.p8"

def get_spotify_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return res.json()["access_token"]

def get_apple_music_token():
    """Generate Apple Music API token using JWT"""
    try:
        # Read the private key
        with open(APPLE_PRIVATE_KEY_PATH, 'r') as f:
            private_key = f.read()
        
        # Create JWT payload (using your exact format)
        payload = {
            'iss': APPLE_TEAM_ID,
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600,  # 1 hour
        }
        
        # Generate JWT token (using your exact format)
        token = jwt.encode(
            payload,
            private_key,
            algorithm='ES256',
            headers={'kid': APPLE_KEY_ID, 'alg': 'ES256'}
        )
        return token
    
    except Exception as e:
        print(f"Error generating Apple Music token: {e}")
        return None

def search_apple_music_track(isrc, token):
    """Search for a track in Apple Music using ISRC"""
    if not isrc or not token:
        return None
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # Search using ISRC
        url = f"https://api.music.apple.com/v1/catalog/us/songs"
        params = {'filter[isrc]': isrc}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                return data['data'][0]  # Return first match
        
        return None
    
    except Exception as e:
        print(f"Error searching Apple Music for ISRC {isrc}: {e}")
        return None

def get_writer_credits(apple_music_id, token):
    """Get writer credits for a track from Apple Music"""
    if not apple_music_id or not token:
        return []
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # Get detailed track info including songwriting credits
        url = f"https://api.music.apple.com/v1/catalog/us/songs/{apple_music_id}"
        params = {'include': 'albums'}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            track_data = data.get('data', [{}])[0]
            attributes = track_data.get('attributes', {})
            
            # Extract writer credits from various fields
            writers = []
            
            # Check composerName field
            if 'composerName' in attributes and attributes['composerName']:
                writers.extend([w.strip() for w in attributes['composerName'].split(',')])
            
            # Check songwriters in editorial notes if available
            editorial_notes = attributes.get('editorialNotes', {})
            if 'short' in editorial_notes:
                # Parse potential writer info from editorial notes
                pass
            
            return list(set(writers))  # Remove duplicates
        
        return []
    
    except Exception as e:
        print(f"Error getting writer credits for Apple Music ID {apple_music_id}: {e}")
        return []

def get_playlists_from_category(market, genre, token):
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
    playlists = []
    
    # Cast a wider net with multiple search strategies
    search_queries = [
        f"{market_code} {genre.lower()}",  # Original approach: "FR hip-hop", "JP pop"
        f"{genre.lower()}",                # Just genre: "pop", "hip-hop" (catches big generic playlists)
        f"{market.lower()} {genre.lower()}" # Full market name: "japan pop", "france hip-hop"
    ]
    
    all_items = []
    seen_ids = set()
    
    for search_query in search_queries:
        search_params = {
            "q": search_query,
            "type": "playlist",
            "market": market_code,
            "limit": 20
        }
        
        search_response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=search_params
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            search_items = search_data.get("playlists", {}).get("items", [])
            
            # Add unique items only
            for item in search_items:
                if item and item.get("id") not in seen_ids:
                    all_items.append(item)
                    seen_ids.add(item.get("id"))
    
    search_items = all_items[:30]  # Keep more results to increase chance of finding big playlists
    
    for item in search_items:
            if not item:
                continue
            
            playlist_id = item.get("id")
            
            # Get follower count for frontend display
            playlist_details = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist_id}",
                headers=headers
            ).json()
            
            playlists.append({
                "playlist_name": item.get("name"),
                "playlist_id": playlist_id,
                "owner": item.get("owner", {}).get("display_name", "Unknown"),
                "followers": playlist_details.get("followers", {}).get("total", 0),
                "description": item.get("description", "")
            })
    
    # Don't sort - keep Spotify's original ranking like your script
    
    return playlists

def get_playlist_tracks_detailed(playlist_id, token, playlist_name=""):
    """Return list of detailed track info for one playlist."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get playlist info (for followers)
    playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    p_info = requests.get(playlist_url, headers=headers).json()
    followers = p_info.get("followers", {}).get("total")
    
    # Get tracks with pagination
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"limit": 100}
    all_tracks = []
    
    while url:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            break
            
        data = r.json()
        
        for item in data.get("items", []):
            track = item.get("track")
            if not track:
                continue
            
            # Extract track details
            isrc = track.get("external_ids", {}).get("isrc")
            track_name = track.get("name")
            artists = ", ".join([a["name"] for a in track.get("artists", [])])
            release_date = track.get("album", {}).get("release_date")
            track_popularity = track.get("popularity")
            spotify_link = track.get("external_urls", {}).get("spotify")
            added_at = item.get("added_at")
            
            all_tracks.append({
                "playlist_name": playlist_name or p_info.get("name"),
                "playlist_id": playlist_id,
                "playlist_followers": followers,
                "track_name": track_name,
                "track_artist": artists,
                "track_added_at": added_at,
                "track_release_date": release_date,
                "track_popularity": track_popularity,
                "isrc": isrc,
                "spotify_link": spotify_link
            })
        
        url = data.get("next")  # Pagination
        time.sleep(0.1)  # Rate limiting
    
    return all_tracks

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    market = data.get('market')
    genre = data.get('genre')
    
    if not market or not genre:
        return jsonify({'error': 'Market and genre required'}), 400
    
    try:
        token = get_spotify_token()
        playlists = get_playlists_from_category(market, genre, token)
        
        # Keep original order like your script
        
        return jsonify({
            'success': True,
            'market': market,
            'genre': genre,
            'playlists_found': len(playlists),
            'playlists': playlists[:10]  # Return top 10
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlist-tracks', methods=['POST'])
def get_tracks():
    data = request.json
    playlist_ids = data.get('playlist_ids', [])
    
    if not playlist_ids:
        return jsonify({'error': 'playlist_ids required'}), 400
    
    try:
        token = get_spotify_token()
        all_tracks = []
        
        for i, playlist_id in enumerate(playlist_ids):
            # Get playlist name first
            playlist_response = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if playlist_response.status_code == 200:
                playlist_data = playlist_response.json()
                playlist_name = playlist_data.get("name", "Unknown")
                
                # Get tracks for this playlist
                tracks = get_playlist_tracks_detailed(playlist_id, token, playlist_name)
                all_tracks.extend(tracks)
                
                # Progress indicator
                print(f"✅ [{i+1}/{len(playlist_ids)}] Fetched {len(tracks)} tracks from '{playlist_name}'")
        
        return jsonify({
            'success': True,
            'total_tracks': len(all_tracks),
            'tracks': all_tracks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enrich-tracks', methods=['POST'])
def enrich_tracks():
    """Enrich Spotify tracks with Apple Music writer credits"""
    data = request.json
    tracks = data.get('tracks', [])
    
    if not tracks:
        return jsonify({'error': 'tracks required'}), 400
    
    try:
        # Generate Apple Music token
        apple_token = get_apple_music_token()
        
        if not apple_token:
            return jsonify({'error': 'Could not generate Apple Music token'}), 500
        
        enriched_tracks = []
        total_tracks = len(tracks)
        
        for i, track in enumerate(tracks):
            enriched_track = track.copy()  # Start with original Spotify data
            
            # Try to get writer credits from Apple Music using ISRC
            isrc = track.get('isrc')
            writers = []
            
            if isrc:
                apple_track = search_apple_music_track(isrc, apple_token)
                if apple_track:
                    apple_id = apple_track.get('id')
                    writers = get_writer_credits(apple_id, apple_token)
            
            # Add writer credits to track data
            enriched_track['writers'] = writers
            enriched_track['writer_count'] = len(writers)
            
            enriched_tracks.append(enriched_track)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"🎵 [{i+1}/{total_tracks}] Enriched tracks with writer credits...")
            
            # Rate limiting for Apple Music API
            time.sleep(0.2)
        
        return jsonify({
            'success': True,
            'total_tracks': len(enriched_tracks),
            'tracks_with_writers': len([t for t in enriched_tracks if t.get('writers')]),
            'tracks': enriched_tracks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)