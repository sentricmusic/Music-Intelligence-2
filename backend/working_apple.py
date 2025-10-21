"""
APPLE MUSIC API EXAMPLES & REFERENCE

PURPOSE:
Reference script demonstrating basic Apple Music API functionality.
Use this to understand how to authenticate and make basic API calls.

WHAT IT CONTAINS:
- JWT token generation for Apple Music API
- Chart data retrieval (top songs, albums, etc.)
- Music search functionality  
- Genre browsing
- Basic song information lookup

USAGE:
python apple_music_examples.py

This script will:
1. Generate Apple Music API token
2. Fetch current chart data
3. Search for songs
4. Display genre information
5. Show example API responses

NOTE: This is for REFERENCE/LEARNING only. 
For production IPI extraction, use direct_snowflake_pipeline.py

REQUIREMENTS:
- AuthKey_FH2F6F277R.p8 (Apple Music API private key)
- Python packages: jwt, requests, json

API CREDENTIALS:
- Team ID: 2MQ6NB4Q3C
- Key ID: FH2F6F277R
- Private Key: AuthKey_FH2F6F277R.p8
"""

import jwt
import time
import requests
import json

# Apple Music API Configuration
KEY_ID = "FH2F6F277R"
TEAM_ID = "2MQ6NB4Q3C"
PRIVATE_KEY_PATH = "AuthKey_FH2F6F277R.p8"

# Load the private key
with open(PRIVATE_KEY_PATH, "r") as f:
    private_key = f.read()

def generate_apple_music_token():
    """Generate JWT token for Apple Music API"""
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

# Common Apple Music API operations
def search_music(query, types="songs", limit=5):
    """Search for music in Apple Music catalog"""
    token = generate_apple_music_token()
    
    url = "https://api.music.apple.com/v1/catalog/us/search"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'term': query,
        'types': types,
        'limit': limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response

def get_charts(types="songs", genre="20"):  # 20 = Alternative music
    """Get music charts"""
    token = generate_apple_music_token()
    
    url = f"https://api.music.apple.com/v1/catalog/us/charts"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'types': types,
        'genre': genre,
        'limit': 10
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response

def get_genres():
    """Get available genres"""
    token = generate_apple_music_token()
    
    url = "https://api.music.apple.com/v1/catalog/us/genres"
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url, headers=headers)
    return response

# Test different operations
print("🎵 APPLE MUSIC API - PRACTICAL EXAMPLES")
print("=" * 50)

# Test 1: Search for music
print("1. 🔍 SEARCHING FOR MUSIC")
print("-" * 25)
try:
    response = search_music("Taylor Swift", "songs", 3)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        songs = data.get('results', {}).get('songs', {}).get('data', [])
        for song in songs:
            print(f"  ♪ {song['attributes']['name']} - {song['attributes']['artistName']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n2. 📈 GETTING CHARTS")
print("-" * 25)
try:
    response = get_charts("songs")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        charts = data.get('results', {}).get('songs', [])
        if charts:
            songs = charts[0].get('data', [])[:5]  # Top 5
            print("Top 5 songs:")
            for i, song in enumerate(songs, 1):
                print(f"  {i}. {song['attributes']['name']} - {song['attributes']['artistName']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n3. 🎭 GETTING GENRES")
print("-" * 25)
try:
    response = get_genres()
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        genres = data.get('data', [])[:10]  # First 10 genres
        print("Available genres:")
        for genre in genres:
            print(f"  - {genre['attributes']['name']} (ID: {genre['id']})")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print(f"\n🎯 WHAT CAN YOU DO WITH APPLE MUSIC API?")
print("- Search for songs, albums, artists, playlists")
print("- Get music charts and trending content")
print("- Access genre information")
print("- Get detailed metadata about music")
print("- For user data (playlists, library), you need user authorization")
print("\n📖 Documentation: https://developer.apple.com/documentation/applemusicapi")