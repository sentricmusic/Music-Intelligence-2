from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import time
import requests
import json
import os
import base64

app = Flask(__name__)
CORS(app)

# Spotify credentials from environment variables
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

# Apple Music credentials from environment variables
KEY_ID = os.environ.get("APPLE_MUSIC_KEY_ID", "FH2F6F277R")
TEAM_ID = os.environ.get("APPLE_MUSIC_TEAM_ID", "2MQ6NB4Q3C")

# Apple Music private key from environment variable
PRIVATE_KEY = os.environ.get("APPLE_MUSIC_PRIVATE_KEY", "")

def generate_apple_music_token():
    """Generate JWT token for Apple Music API"""
    payload = {
        'iss': TEAM_ID,
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,  # 1 hour
    }

    return jwt.encode(
        payload,
        PRIVATE_KEY,
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
    """Enhanced lookup with IPI extraction"""
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

                # Extract main artist IPI from artistUrl
                artist_url = attributes.get('artistUrl', '')
                if artist_url:
                    artist_ipi_match = re.search(r'/artist/[^/]+/(\d{9,11})$', artist_url)
                    if artist_ipi_match:
                        result['main_artist_ipi'] = artist_ipi_match.group(1)
                        result['all_ipi_numbers'].append(artist_ipi_match.group(1))

                # Search for individual writer IPIs
                composer_name = attributes.get('composerName', '')
                if composer_name:
                    writers = re.split(r'[&,]', composer_name)
                    writers = [w.strip() for w in writers if w.strip()]

                    for writer in writers[:3]:  # Limit to first 3 writers
                        try:
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
                            
                            time.sleep(0.1)
                            
                        except Exception as e:
                            print(f"Error searching for writer {writer}: {e}")
                            continue

                # Count composers
                composer_count = 0
                if composer_name:
                    composers = [name.strip() for name in composer_name.replace('&', ',').split(',')]
                    composer_count = len([c for c in composers if c])
                
                result['composer_count'] = composer_count
                
                if result['composer_names'] or result['main_artist_ipi'] or result['writer_ipis']:
                    result['api_status'] = 'found_with_credits'
                
                result['total_ipis_found'] = len(result['all_ipi_numbers'])
                result['all_ipi_string'] = ','.join(result['all_ipi_numbers']) if result['all_ipi_numbers'] else None
                
                return result
            else:
                return {'api_status': 'not_found', 'isrc': isrc}
        else:
            return {'api_status': 'error', 'isrc': isrc}
            
    except Exception as e:
        return {'api_status': 'error', 'isrc': isrc, 'error': str(e)}

@app.route('/api/test', methods=['GET'])
def test():
    """Test API endpoints"""
    try:
        token = generate_apple_music_token()
        test_result = search_apple_music_by_isrc("USRC17607839")
        
        return jsonify({
            'success': True,
            'message': 'API working!',
            'token_generated': bool(token),
            'test_search': test_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Import the rest of your playlist discovery logic here...
# (I'll include the key functions to keep it working)

def get_playlists_from_category(market, genre, token):
    """Your complete playlist discovery system"""
    # [Include your full market_config and playlist logic here]
    # For brevity, I'm showing the structure - you'd copy the full function
    
    market_config = {
        'France': {'code': 'FR', 'terms': ['français', 'french', 'france', 'fr']},
        'UK': {'code': 'GB', 'terms': ['uk', 'british', 'britain', 'gb']},
        'US': {'code': 'US', 'terms': ['american', 'usa', 'us']},
        # ... all your other markets
    }
    
    # Your complete playlist search logic goes here
    return []  # Placeholder - include your full logic

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Get Spotify playlists"""
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
            'playlists': playlists[:10]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel handler
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)