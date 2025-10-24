#!/usr/bin/env python3
"""
Comprehensive test script to validate all market/genre combinations
Tests the universal playlist discovery system
"""

import requests
import json
import time
from datetime import datetime

# Test combinations to validate
TEST_COMBINATIONS = [
    # Core markets we've been working with
    ("France", "hip-hop"),
    ("UK", "electronic"),
    ("Germany", "hip-hop"),
    ("Spain", "pop"),
    ("US", "hip-hop"),
    ("Japan", "pop"),
    ("Thailand", "pop"),
    
    # Additional combinations to test
    ("France", "pop"),
    ("UK", "hip-hop"),
    ("Germany", "electronic"), 
    ("Italy", "pop"),
    ("Netherlands", "electronic"),
    ("Sweden", "pop"),
    ("Norway", "electronic"),
    ("Brazil", "hip-hop"),
    ("Mexico", "pop"),
    ("Australia", "rock"),
    ("Canada", "hip-hop"),
    ("South Korea", "pop"),
]

def test_combination(market, genre):
    """Test a specific market/genre combination"""
    try:
        url = "http://localhost:5001/api/analyze"
        payload = {"market": market, "genre": genre}
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            playlists = data.get('playlists', [])
            
            print(f"\n🎵 {market} - {genre.title()}")
            print(f"   Status: ✅ SUCCESS ({len(playlists)} playlists)")
            
            # Show top 3 playlists for quality check
            for i, playlist in enumerate(playlists[:3]):
                name = playlist.get('playlist_name', 'Unknown')
                followers = playlist.get('followers', 0)
                print(f"   {i+1}. {name} ({followers:,} followers)")
            
            return {
                'market': market,
                'genre': genre, 
                'status': 'success',
                'count': len(playlists),
                'playlists': playlists[:3]  # Top 3 for analysis
            }
        else:
            print(f"\n❌ {market} - {genre.title()}")
            print(f"   Error: {response.status_code} - {response.text}")
            return {
                'market': market,
                'genre': genre,
                'status': 'error',
                'error': f"{response.status_code}: {response.text}"
            }
            
    except Exception as e:
        print(f"\n💥 {market} - {genre.title()}")
        print(f"   Exception: {str(e)}")
        return {
            'market': market,
            'genre': genre,
            'status': 'exception',
            'error': str(e)
        }

def analyze_results(results):
    """Analyze the quality of results for each market/genre"""
    
    print(f"\n{'='*60}")
    print(f"🔍 QUALITY ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    success_count = 0
    total_count = len(results)
    
    # Group by market for analysis
    markets = {}
    for result in results:
        if result['market'] not in markets:
            markets[result['market']] = []
        markets[result['market']].append(result)
    
    for market, market_results in markets.items():
        print(f"\n🌍 {market.upper()}")
        
        for result in market_results:
            if result['status'] == 'success':
                success_count += 1
                genre = result['genre']
                count = result['count']
                playlists = result['playlists']
                
                print(f"  ✅ {genre.title()}: {count} playlists found")
                
                # Quality indicators
                quality_indicators = []
                
                for playlist in playlists:
                    name = playlist.get('playlist_name', '').lower()
                    
                    # Check for market-specific terms
                    market_terms = {
                        'France': ['français', 'french', 'france'],
                        'Germany': ['deutsch', 'german', 'deutschland'], 
                        'Spain': ['español', 'spanish', 'españa'],
                        'UK': ['uk', 'british', 'britain'],
                        'Japan': ['j-', 'japanese', 'japan'],
                        'Italy': ['italian', 'italiano', 'italy'],
                        'Netherlands': ['dutch', 'nederlands', 'holland'],
                        'Sweden': ['swedish', 'svensk', 'sweden'],
                        'Brazil': ['brazilian', 'brasil', 'brazil'],
                        'South Korea': ['k-', 'korean', 'korea']
                    }
                    
                    market_specific = any(term in name for term in market_terms.get(market, []))
                    
                    # Check for genre relevance
                    genre_relevant = genre.lower() in name or any(
                        g in name for g in ['rap', 'pop', 'electronic', 'rock', 'hip', 'dance']
                    )
                    
                    # Quality scoring
                    score = 0
                    if market_specific: score += 2
                    if genre_relevant: score += 1
                    if playlist.get('followers', 0) > 1000: score += 1
                    
                    quality_indicators.append(score)
                
                avg_quality = sum(quality_indicators) / len(quality_indicators) if quality_indicators else 0
                quality_grade = "🟢 EXCELLENT" if avg_quality >= 3 else "🟡 GOOD" if avg_quality >= 2 else "🔴 NEEDS WORK"
                
                print(f"     Quality: {quality_grade} (Score: {avg_quality:.1f}/4)")
                
            else:
                print(f"  ❌ {result['genre'].title()}: {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"   Total Combinations Tested: {total_count}")
    
    return success_count/total_count >= 0.9  # 90% success rate threshold

def main():
    print("🚀 Starting Comprehensive Market/Genre Testing...")
    print(f"Testing {len(TEST_COMBINATIONS)} combinations")
    
    results = []
    
    for i, (market, genre) in enumerate(TEST_COMBINATIONS):
        print(f"\nTesting {i+1}/{len(TEST_COMBINATIONS)}: {market} - {genre}")
        
        result = test_combination(market, genre)
        results.append(result)
        
        # Rate limiting to avoid overwhelming the API
        time.sleep(2)
    
    # Analyze results
    is_passing = analyze_results(results)
    
    # Save detailed results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    if is_passing:
        print("🎉 UNIVERSAL SYSTEM: PASSING! All markets/genres working correctly.")
    else:
        print("⚠️  UNIVERSAL SYSTEM: NEEDS IMPROVEMENT. Some combinations failing.")
    print(f"{'='*60}")
    
    return is_passing

if __name__ == "__main__":
    main()