from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import time
import requests
import json
import os
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Spotify credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Your exact working Apple Music credentials
KEY_ID = "FH2F6F277R"
TEAM_ID = "2MQ6NB4Q3C"
PRIVATE_KEY_PATH = "AuthKey_FH2F6F277R.p8"

# Load the private key (your exact method)
with open(PRIVATE_KEY_PATH, "r") as f:
    private_key = f.read()

def generate_apple_music_token():
    """Generate JWT token for Apple Music API - YOUR EXACT WORKING CODE"""
    payload = {
        'iss': TEAM_ID,
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,  # 1 hour
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm='ES256',
        headers={'kid': KEY_ID, 'alg': 'ES256'}
    )

def get_spotify_token():
    """Get Spotify access token"""
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return res.json()["access_token"]

def search_apple_music_by_isrc(isrc):
    """Enhanced lookup with IPI extraction - YOUR EXACT PRODUCTION CODE"""
    import re
    
    token = generate_apple_music_token()
    
    url = "https://api.music.apple.com/v1/catalog/us/songs"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'filter[isrc]': isrc,
        'include': 'artists,albums,composers',
        'extend': 'editorialNotes,offers,artistUrl,popularity'
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                song = data['data'][0]
                attributes = song.get('attributes', {})
                
                result = {
                    'isrc': isrc,
                    'track_name': attributes.get('name', ''),
                    'artist_name': attributes.get('artistName', ''),
                    'composer_names': attributes.get('composerName', ''),
                    'apple_music_url': attributes.get('url', ''),
                    'genre_names': ', '.join(attributes.get('genreNames', [])),
                    'main_artist_ipi': None,
                    'writer_ipis': [],
                    'all_ipi_numbers': [],
                    'api_status': 'found'
                }

                # Extract main artist IPI from artistUrl (YOUR EXACT METHOD)
                artist_url = attributes.get('artistUrl', '')
                if artist_url:
                    artist_ipi_match = re.search(r'/artist/[^/]+/(\d{9,11})$', artist_url)
                    if artist_ipi_match:
                        result['main_artist_ipi'] = artist_ipi_match.group(1)
                        result['all_ipi_numbers'].append(artist_ipi_match.group(1))

                # Search for individual writer IPIs (YOUR EXACT METHOD)
                composer_name = attributes.get('composerName', '')
                if composer_name:
                    writers = re.split(r'[&,]', composer_name)
                    writers = [w.strip() for w in writers if w.strip()]

                    for writer in writers[:3]:  # Limit to first 3 writers
                        try:
                            # Search for writer in Apple Music
                            search_params = {
                                'term': writer,
                                'types': 'artists',
                                'limit': 5
                            }
                            
                            search_response = requests.get(
                                "https://api.music.apple.com/v1/catalog/us/search",
                                headers=headers,
                                params=search_params
                            )
                            
                            if search_response.status_code == 200:
                                search_data = search_response.json()
                                artists = search_data.get('results', {}).get('artists', {}).get('data', [])
                                
                                for artist in artists:
                                    artist_attrs = artist.get('attributes', {})
                                    artist_name = artist_attrs.get('name', '')
                                    writer_url = artist_attrs.get('url', '')
                                    
                                    # Check if this artist matches our writer
                                    if (writer.lower() == artist_name.lower() or 
                                        artist_name.lower() in writer.lower()):
                                        
                                        writer_ipi_match = re.search(r'/artist/[^/]+/(\d{9,11})$', writer_url)
                                        if writer_ipi_match:
                                            writer_ipi = writer_ipi_match.group(1)
                                            result['writer_ipis'].append({
                                                'name': writer,
                                                'ipi': writer_ipi,
                                                'found_as': artist_name
                                            })
                                            result['all_ipi_numbers'].append(writer_ipi)
                                            break
                            
                            time.sleep(0.1)  # Rate limiting for writer searches
                            
                        except Exception as e:
                            print(f"Error searching for writer {writer}: {e}")
                            continue

                # Count composers
                composer_count = 0
                if composer_name:
                    composers = [name.strip() for name in composer_name.replace('&', ',').split(',')]
                    composer_count = len([c for c in composers if c])
                
                result['composer_count'] = composer_count
                
                # Set final status based on credits found
                if result['composer_names'] or result['main_artist_ipi'] or result['writer_ipis']:
                    result['api_status'] = 'found_with_credits'
                
                # Add IPI summary fields
                result['total_ipis_found'] = len(result['all_ipi_numbers'])
                result['all_ipi_string'] = ','.join(result['all_ipi_numbers']) if result['all_ipi_numbers'] else None
                
                return result
            else:
                return {'api_status': 'not_found', 'isrc': isrc}
        else:
            print(f"Apple Music API error for ISRC {isrc}: {response.status_code}")
            return {'api_status': 'error', 'isrc': isrc}
            
    except Exception as e:
        print(f"Error searching Apple Music for ISRC {isrc}: {e}")
        return {'api_status': 'error', 'isrc': isrc, 'error': str(e)}

@app.route('/api/test', methods=['GET'])
def test():
    """Test both token generation and ISRC search"""
    try:
        token = generate_apple_music_token()
        
        # Test with a real ISRC
        test_result = search_apple_music_by_isrc("USRC17607839")  # Taylor Swift example
        
        return jsonify({
            'success': True,
            'message': 'Apple Music API working!',
            'token_generated': bool(token),
            'token_length': len(str(token)) if token else 0,
            'test_search': test_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_playlists_from_category(market, genre, token):
    """Get real Spotify playlists based on market and genre"""
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
    
    # Multiple search strategies to find relevant playlists
    search_queries = [
        f"{market_code} {genre.lower()}",  # "FR hip-hop", "JP pop"
        f"{genre.lower()}",                # Just genre: "pop", "hip-hop" 
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
    
    search_items = all_items[:30]  # Keep more results to find bigger playlists
    
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
    
    # Sort by follower count (biggest playlists first)
    playlists.sort(key=lambda x: x.get("followers", 0), reverse=True)
    
    return playlists

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Get real Spotify playlists for market and genre"""
    data = request.json
    market = data.get('market')
    genre = data.get('genre')
    
    if not market or not genre:
        return jsonify({'error': 'Market and genre required'}), 400
    
    try:
        token = get_spotify_token()
        playlists = get_playlists_from_category(market, genre, token)
        
        return jsonify({
            'success': True,
            'market': market,
            'genre': genre,
            'playlists_found': len(playlists),
            'playlists': playlists[:10]  # Return top 10
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/playlist-tracks', methods=['POST'])
def get_playlist_tracks():
    """Get real Spotify track details from playlists"""
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

@app.route('/api/writer-credits', methods=['POST'])
def get_writer_credits():
    """Get writer credits using your exact working Apple Music setup"""
    try:
        data = request.json
        tracks = data.get('tracks', [])
        
        if not tracks:
            return jsonify({'error': 'tracks required'}), 400
        
        enriched_tracks = []
        stats = {
            'total_processed': 0,
            'found_in_apple_music': 0,
            'has_writer_credits': 0,
            'has_isrc': 0
        }
        
        # Limit to first 10 tracks for faster testing
        limited_tracks = tracks[:10]
        print(f"🔥 FAST MODE: Processing only first 10 tracks (out of {len(tracks)} total)")
        
        for track in limited_tracks:
            stats['total_processed'] += 1
            enriched_track = track.copy()
            
            isrc = track.get('isrc')
            if isrc:
                stats['has_isrc'] += 1
                
                # Use your exact working Apple Music search
                apple_result = search_apple_music_by_isrc(isrc)
                
                enriched_track.update(apple_result)
                
                if apple_result.get('api_status') == 'found':
                    stats['found_in_apple_music'] += 1
                    if apple_result.get('composer_names'):
                        stats['has_writer_credits'] += 1
            else:
                enriched_track.update({'api_status': 'no_isrc'})
            
            enriched_tracks.append(enriched_track)
            
            # Rate limiting
            time.sleep(0.5)
            
            print(f"✅ Processed {stats['total_processed']}/{len(limited_tracks)}: {track.get('track_name', 'Unknown')}")
        
        # Calculate success rates
        success_rate = (stats['found_in_apple_music'] / stats['has_isrc'] * 100) if stats['has_isrc'] > 0 else 0
        credits_rate = (stats['has_writer_credits'] / stats['has_isrc'] * 100) if stats['has_isrc'] > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_processed': stats['total_processed'],
                'has_isrc': stats['has_isrc'],
                'found_in_apple_music': stats['found_in_apple_music'],
                'has_writer_credits': stats['has_writer_credits'],
                'apple_music_success_rate': f"{success_rate:.1f}%",
                'writer_credits_rate': f"{credits_rate:.1f}%"
            },
            'tracks': enriched_tracks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting WORKING Apple Music Server...")
    print(f"📁 Apple Music key exists: {os.path.exists(PRIVATE_KEY_PATH)}")
    
    # Test Apple Music on startup
    try:
        token = generate_apple_music_token()
        print(f"✅ Apple Music token generated: {str(token)[:50]}...")
    except Exception as e:
        print(f"❌ Apple Music setup failed: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5001)  # Different port to avoid conflicts