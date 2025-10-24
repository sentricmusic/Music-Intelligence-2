from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os
import time
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Apple Music credentials from your production implementation
APPLE_TEAM_ID = "2MQ6NB4Q3C"
APPLE_KEY_ID = "FH2F6F277R"
APPLE_PRIVATE_KEY_PATH = "AuthKey_FH2F6F277R.p8"

def get_spotify_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return res.json()["access_token"]

def generate_apple_music_token():
    """Generate JWT token for Apple Music API - matches your exact production code"""
    try:
        with open(APPLE_PRIVATE_KEY_PATH, 'r') as key_file:
            private_key = key_file.read()
        
        headers = {
            'alg': 'ES256',
            'kid': APPLE_KEY_ID
        }

        payload = {
            'iss': APPLE_TEAM_ID,
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600
        }

        token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
        print("✅ Apple Music token generated successfully")
        return token
    except Exception as e:
        print(f"❌ Error generating Apple Music token: {e}")
        return None

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify server is working"""
    try:
        spotify_token = get_spotify_token()
        apple_token = generate_apple_music_token()
        
        return jsonify({
            'success': True,
            'message': 'Backend server is running!',
            'timestamp': datetime.now().isoformat(),
            'spotify_token_length': len(spotify_token) if spotify_token else 0,
            'apple_token_length': len(str(apple_token)) if apple_token else 0,
            'apple_music_key_exists': os.path.exists(APPLE_PRIVATE_KEY_PATH)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    return jsonify({
        'success': True,
        'message': 'Analyze endpoint - under construction'
    })

if __name__ == '__main__':
    print("🚀 Starting Music Intelligence Backend Server (Working Version)...")
    print(f"📁 Looking for Apple Music key at: {APPLE_PRIVATE_KEY_PATH}")
    print(f"🔑 Key file exists: {os.path.exists(APPLE_PRIVATE_KEY_PATH)}")
    print(f"📊 Spotify credentials loaded: {bool(CLIENT_ID and CLIENT_SECRET)}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)