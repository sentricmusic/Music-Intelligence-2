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
    """Universal playlist discovery system - works intelligently for ALL markets and genres"""
    
    # Market configurations with local terms
    market_config = {
        'France': {
            'code': 'FR',
            'terms': ['français', 'french', 'france', 'fr'],
            'genre_translations': {
                'hip-hop': ['rap français', 'rap fr', 'rappeur français'],
                'pop': ['pop français', 'chanson française', 'pop fr'],
                'electronic': ['électro français', 'french electronic', 'électro fr'],
                'rock': ['rock français', 'french rock', 'rock fr'],
                'r&b': ['rnb français', 'french rnb', 'rnb fr']
            }
        },
        'Germany': {
            'code': 'DE',
            'terms': ['deutsch', 'german', 'deutschland', 'de'],
            'genre_translations': {
                'hip-hop': ['deutscher rap', 'rap deutsch', 'german rap'],
                'pop': ['deutscher pop', 'german pop', 'pop deutsch'],
                'electronic': ['deutsche elektronik', 'german electronic', 'techno deutsch'],
                'rock': ['deutscher rock', 'german rock', 'rock deutsch'],
                'r&b': ['deutscher rnb', 'german rnb', 'rnb deutsch']
            }
        },
        'Spain': {
            'code': 'ES',
            'terms': ['español', 'spanish', 'españa', 'es'],
            'genre_translations': {
                'hip-hop': ['rap español', 'rap españa', 'spanish rap'],
                'pop': ['pop español', 'spanish pop', 'pop españa'],
                'electronic': ['electrónica española', 'spanish electronic', 'electro españa'],
                'rock': ['rock español', 'spanish rock', 'rock españa'],
                'r&b': ['rnb español', 'spanish rnb', 'rnb españa']
            }
        },
        'UK': {
            'code': 'GB',
            'terms': ['uk', 'british', 'britain', 'gb'],
            'genre_translations': {
                'hip-hop': ['uk rap', 'british rap', 'grime uk'],
                'pop': ['uk pop', 'british pop', 'brit pop'],
                'electronic': ['uk house', 'uk dance', 'british electronic', 'uk garage', 'uk bass', 'uk bassline', 'uk dnb', 'uk dubstep'],
                'rock': ['uk rock', 'british rock', 'brit rock'],
                'r&b': ['uk rnb', 'british rnb', 'uk soul']
            }
        },
        'US': {
            'code': 'US',
            'terms': ['american', 'usa', 'us'],
            'genre_translations': {
                'hip-hop': ['american rap', 'us hip hop', 'usa rap'],
                'pop': ['american pop', 'us pop', 'usa pop'],
                'electronic': ['american edm', 'us electronic', 'usa dance'],
                'rock': ['american rock', 'us rock', 'usa rock'],
                'r&b': ['american rnb', 'us rnb', 'usa soul']
            }
        },
        'Thailand': {
            'code': 'TH',
            'terms': ['thai', 'thailand', 'th'],
            'genre_translations': {
                'hip-hop': ['thai rap', 'thailand hip hop', 'thai hip hop'],
                'pop': ['thai pop', 'thailand pop', 't-pop'],
                'electronic': ['thai electronic', 'thailand dance', 'thai edm'],
                'rock': ['thai rock', 'thailand rock', 'thai indie'],
                'r&b': ['thai rnb', 'thailand rnb', 'thai soul']
            }
        },
        'Japan': {
            'code': 'JP',
            'terms': ['japanese', 'japan', 'jp', 'j-'],
            'genre_translations': {
                'hip-hop': ['japanese rap', 'japan hip hop', 'j-rap'],
                'pop': ['j-pop', 'japanese pop', 'japan pop'],
                'electronic': ['japanese electronic', 'japan edm', 'j-electronic'],
                'rock': ['j-rock', 'japanese rock', 'japan rock'],
                'r&b': ['j-rnb', 'japanese rnb', 'japan soul']
            }
        },
        'Italy': {
            'code': 'IT',
            'terms': ['italian', 'italiano', 'italy', 'it'],
            'genre_translations': {
                'hip-hop': ['rap italiano', 'italian rap', 'rap italia'],
                'pop': ['pop italiano', 'italian pop', 'musica italiana'],
                'electronic': ['elettronica italiana', 'italian electronic'],
                'rock': ['rock italiano', 'italian rock'],
                'r&b': ['rnb italiano', 'italian rnb']
            }
        },
        'Netherlands': {
            'code': 'NL',
            'terms': ['dutch', 'nederlands', 'holland', 'nl'],
            'genre_translations': {
                'hip-hop': ['nederlandse rap', 'dutch rap', 'nl rap'],
                'pop': ['nederlandse pop', 'dutch pop', 'nl pop'],
                'electronic': ['dutch electronic', 'nederlands dance'],
                'rock': ['nederlandse rock', 'dutch rock'],
                'r&b': ['nederlandse rnb', 'dutch rnb']
            }
        },
        'Sweden': {
            'code': 'SE',
            'terms': ['swedish', 'sverige', 'sweden', 'se'],
            'genre_translations': {
                'hip-hop': ['svensk rap', 'swedish rap', 'sverige rap'],
                'pop': ['svensk pop', 'swedish pop', 'sverige pop'],
                'electronic': ['svensk elektronisk', 'swedish electronic'],
                'rock': ['svensk rock', 'swedish rock'],
                'r&b': ['svensk rnb', 'swedish rnb']
            }
        },
        'Norway': {
            'code': 'NO',
            'terms': ['norwegian', 'norsk', 'norway', 'no'],
            'genre_translations': {
                'hip-hop': ['norsk rap', 'norwegian rap', 'norge rap'],
                'pop': ['norsk pop', 'norwegian pop'],
                'electronic': ['norsk elektronisk', 'norwegian electronic'],
                'rock': ['norsk rock', 'norwegian rock'],
                'r&b': ['norsk rnb', 'norwegian rnb']
            }
        },
        'Brazil': {
            'code': 'BR',
            'terms': ['brazilian', 'brasil', 'brazil', 'br'],
            'genre_translations': {
                'hip-hop': ['rap brasileiro', 'brazilian rap', 'rap br'],
                'pop': ['pop brasileiro', 'brazilian pop', 'mpb'],
                'electronic': ['eletrônica brasileira', 'brazilian electronic'],
                'rock': ['rock brasileiro', 'brazilian rock'],
                'r&b': ['rnb brasileiro', 'brazilian rnb']
            }
        },
        'Mexico': {
            'code': 'MX',
            'terms': ['mexican', 'méxico', 'mexico', 'mx'],
            'genre_translations': {
                'hip-hop': ['rap mexicano', 'mexican rap', 'rap mx'],
                'pop': ['pop mexicano', 'mexican pop'],
                'electronic': ['electrónica mexicana', 'mexican electronic'],
                'rock': ['rock mexicano', 'mexican rock'],
                'r&b': ['rnb mexicano', 'mexican rnb']
            }
        },
        'Australia': {
            'code': 'AU',
            'terms': ['australian', 'aussie', 'australia', 'au'],
            'genre_translations': {
                'hip-hop': ['australian rap', 'aussie rap', 'au rap'],
                'pop': ['australian pop', 'aussie pop'],
                'electronic': ['australian electronic', 'aussie electronic'],
                'rock': ['australian rock', 'aussie rock'],
                'r&b': ['australian rnb', 'aussie rnb']
            }
        },
        'Canada': {
            'code': 'CA',
            'terms': ['canadian', 'canada', 'ca'],
            'genre_translations': {
                'hip-hop': ['canadian rap', 'canada rap', 'ca rap'],
                'pop': ['canadian pop', 'canada pop'],
                'electronic': ['canadian electronic', 'canada electronic'],
                'rock': ['canadian rock', 'canada rock'],
                'r&b': ['canadian rnb', 'canada rnb']
            }
        },
        'South Korea': {
            'code': 'KR',
            'terms': ['korean', 'korea', 'k-', 'kr'],
            'genre_translations': {
                'hip-hop': ['k-rap', 'korean rap', 'khiphop'],
                'pop': ['k-pop', 'korean pop', 'kpop'],
                'electronic': ['k-electronic', 'korean electronic'],
                'rock': ['k-rock', 'korean rock'],
                'r&b': ['k-rnb', 'korean rnb']
            }
        }
    }
    
    # Get market configuration
    config = market_config.get(market, {'code': market, 'terms': [market.lower()], 'genre_translations': {}})
    market_code = config['code']
    market_terms = config['terms']
    
    headers = {"Authorization": f"Bearer {token}"}
    playlists = []
    
    # Build comprehensive search queries
    search_queries = []
    
    # 1. Local language specific terms (highest priority)
    genre_translations = config['genre_translations'].get(genre.lower(), [])
    search_queries.extend(genre_translations)
    
    # 2. Market + genre combinations  
    for term in market_terms:
        search_queries.append(f"{term} {genre.lower()}")
    
    # 3. Market code + genre
    search_queries.append(f"{market_code} {genre.lower()}")
    
    # 4. Add mainstream search terms for better variety
    if market == 'UK' and genre.lower() == 'electronic':
        # Add mainstream UK dance terms
        mainstream_searches = [
            "uk dance hits",
            "uk house music", 
            "new music friday uk",
            "dance party uk",
            "uk electronic music",
            "british dance music"
        ]
        search_queries.extend(mainstream_searches)
    
    # 5. Generic genre (lowest priority)
    search_queries.append(genre.lower())
    
    # Universal filtering system - automatically works for ALL markets/genres
    def get_universal_skip_terms(market, genre):
        """Generate smart skip terms based on market and genre"""
        # Base terms that are generally irrelevant for music discovery
        base_skip = ['sleep', 'study', 'meditation', 'yoga', 'ambient', 'white noise', 'rain sounds']
        
        # Genre-specific filtering
        genre_skip = []
        if genre.lower() in ['hip-hop', 'rap']:
            genre_skip = ['lofi', 'lo-fi', 'jazz', 'classical', 'instrumental', 'beats to study', 'chill beats']
            # Cross-cultural contamination prevention (unless it's that market)
            if market not in ['South Korea', 'Korea']: 
                genre_skip.extend(['kpop', 'k-pop', 'korean'])
            if market not in ['Japan']: 
                genre_skip.extend(['jpop', 'j-pop', 'anime', 'vocaloid'])
            if market not in ['US', 'USA']: 
                genre_skip.extend(['type beat', 'beats for sale'])
        
        elif genre.lower() == 'electronic':
            genre_skip = ['acoustic', 'unplugged', 'live session', 'classical']
            # For UK electronic, be less aggressive with filtering to allow mainstream dance
            if market == 'UK':
                genre_skip.extend(['ambient', 'meditation', 'sleep'])  # Keep mainstream dance/house
            else:
                if market not in ['Netherlands', 'Belgium']: 
                    genre_skip.extend(['tomorrowland'])
                if market not in ['UK', 'Britain']: 
                    genre_skip.extend(['ministry of sound'])
            
        elif genre.lower() == 'pop':
            genre_skip = ['death metal', 'black metal', 'hardcore punk', 'grindcore']
        
        elif genre.lower() == 'rock':
            genre_skip = ['top 40', 'dance hits', 'club music']
        
        # Add workout/generic playlists that dilute results
        generic_skip = ['workout', 'gym', 'running', 'car music', 'party mix', 'wedding']
        
        return base_skip + genre_skip + generic_skip
    
    def calculate_universal_priority(playlist_name, market, genre, search_query, config):
        """Universal priority calculation that works for any market/genre"""
        priority = 0
        name_lower = playlist_name.lower()
        query_lower = search_query.lower()
        
        # Market-specific boost (highest priority)
        market_terms = config.get('terms', [])
        for term in market_terms:
            if term in name_lower:
                priority += 20  # Strong boost for market-specific playlists
        
        # Genre translation boost (very high priority)
        genre_translations = config.get('genre_translations', {}).get(genre.lower(), [])
        for translation in genre_translations:
            translation_words = translation.split()
            if all(word in name_lower for word in translation_words):
                # Balanced priority: mainstream and underground both get good scores
                if market == 'UK' and genre.lower() == 'electronic':
                    # Give mainstream terms equal priority with underground
                    mainstream_terms = ['uk house', 'uk dance', 'british electronic']
                    underground_terms = ['uk garage', 'uk bass', 'uk bassline']
                    if any(term in translation for term in mainstream_terms):
                        priority += 15  # Equal priority for mainstream
                    elif any(term in translation for term in underground_terms):
                        priority += 15  # Equal priority for underground
                    else:
                        priority += 15
                else:
                    priority += 15  # Strong boost for local language genre terms
        
        # Recency boost
        current_year = "2025"
        recent_terms = [current_year, "2024", "new", "fresh", "latest", "now"]
        if any(term in name_lower for term in recent_terms):
            priority += 8
        
        # Quality indicators boost
        quality_terms = ["best", "top", "hits", "bangers", "essential", "ultimate", "must hear"]
        quality_score = sum(3 for term in quality_terms if term in name_lower)
        priority += min(quality_score, 9)  # Cap quality boost
        
        # Official/curated playlist boost
        official_terms = ["official", "spotify", "curated", "editorial", "new music friday"]
        if any(term in name_lower for term in official_terms):
            priority += 8  # Higher boost for official playlists
        
        # Mainstream UK dance playlist boost
        if market == 'UK' and genre.lower() == 'electronic':
            mainstream_playlist_terms = ["dance hits", "house music", "dance party", "electronic music", "club hits"]
            if any(term in name_lower for term in mainstream_playlist_terms):
                priority += 5  # Boost mainstream dance playlists
        
        return priority
    
    # Execute search with universal logic
    all_items = []
    seen_ids = set()
    
    for search_query in search_queries[:10]:  # Increased for better coverage
        search_params = {
            "q": search_query,
            "type": "playlist", 
            "market": market_code,
            "limit": 25  # Increased limit
        }
        
        try:
            search_response = requests.get(
                "https://api.spotify.com/v1/search",
                headers=headers,
                params=search_params
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                search_items = search_data.get("playlists", {}).get("items", [])
                
                # Add unique items with metadata
                for item in search_items:
                    if item and item.get("id") not in seen_ids:
                        item['_search_query'] = search_query  # Track which query found it
                        all_items.append(item)
                        seen_ids.add(item.get("id"))
        
        except Exception as e:
            print(f"Search error for query '{search_query}': {e}")
            continue
    
    # Process and filter results with universal logic
    processed_playlists = []
    skip_terms = get_universal_skip_terms(market, genre)
    
    for item in all_items[:60]:  # Process more items for better filtering
        if not item:
            continue
            
        playlist_id = item.get("id")
        playlist_name = item.get("name", "")
        name_lower = playlist_name.lower()
        
        # Universal skip check
        should_skip = any(term in name_lower for term in skip_terms)
        if should_skip:
            continue
        
        # Get detailed playlist info
        try:
            playlist_details = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist_id}",
                headers=headers
            ).json()
            
            followers = playlist_details.get("followers", {}).get("total", 0)
            
            # Calculate priority using universal system
            search_query = item.get('_search_query', '')
            priority = calculate_universal_priority(playlist_name, market, genre, search_query, config)
            
            processed_playlists.append({
                "playlist_name": playlist_name,
                "playlist_id": playlist_id,
                "owner": item.get("owner", {}).get("display_name", "Unknown"),
                "followers": followers,
                "description": item.get("description", ""),
                "priority": priority,
                "search_query": search_query
            })
            
        except Exception as e:
            print(f"Error getting playlist details for {playlist_id}: {e}")
            continue
    
    # Universal sorting: priority first, then followers
    processed_playlists.sort(key=lambda x: (x.get('priority', 0), x.get('followers', 0)), reverse=True)
    playlists = processed_playlists
    
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
            'has_any_ipis': 0,
            'total_ipis_found': 0,
            'artist_ipis_found': 0,
            'writer_ipis_found': 0,
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
                
                if apple_result.get('api_status') in ['found', 'found_with_credits']:
                    stats['found_in_apple_music'] += 1
                    
                    # Count traditional writer credits (composer names)
                    if apple_result.get('composer_names'):
                        stats['has_writer_credits'] += 1
                    
                    # Count IPI extractions (main artist + writers)
                    has_any_ipi = False
                    
                    if apple_result.get('main_artist_ipi'):
                        stats['artist_ipis_found'] += 1
                        stats['total_ipis_found'] += 1
                        has_any_ipi = True
                    
                    if apple_result.get('writer_ipis'):
                        for writer in apple_result.get('writer_ipis', []):
                            if writer.get('ipi'):
                                stats['writer_ipis_found'] += 1
                                stats['total_ipis_found'] += 1
                                has_any_ipi = True
                    
                    if has_any_ipi:
                        stats['has_any_ipis'] += 1
            else:
                enriched_track.update({'api_status': 'no_isrc'})
            
            enriched_tracks.append(enriched_track)
            
            # Rate limiting
            time.sleep(0.5)
            
            print(f"✅ Processed {stats['total_processed']}/{len(limited_tracks)}: {track.get('track_name', 'Unknown')}")
        
        # Calculate success rates
        success_rate = (stats['found_in_apple_music'] / stats['has_isrc'] * 100) if stats['has_isrc'] > 0 else 0
        credits_rate = (stats['has_writer_credits'] / stats['has_isrc'] * 100) if stats['has_isrc'] > 0 else 0
        ipi_success_rate = (stats['has_any_ipis'] / stats['has_isrc'] * 100) if stats['has_isrc'] > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_processed': stats['total_processed'],
                'has_isrc': stats['has_isrc'],
                'found_in_apple_music': stats['found_in_apple_music'],
                'has_writer_credits': stats['has_writer_credits'],
                'apple_music_success_rate': f"{success_rate:.1f}%",
                'writer_credits_rate': f"{credits_rate:.1f}%",
                'total_ipis_found': stats['total_ipis_found'],
                'artist_ipis_found': stats['artist_ipis_found'],
                'writer_ipis_found': stats['writer_ipis_found'],
                'ipi_success_rate': f"{ipi_success_rate:.1f}%",
                'has_any_ipis': stats['has_any_ipis']
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