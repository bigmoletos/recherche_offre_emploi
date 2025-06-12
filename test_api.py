#!/usr/bin/env python3
import requests
import json

# Test de l'API POST /scrape-offres
url = "http://localhost:9555/scrape-offres"
data = {
    "termes": ["alternance cybersécurité"],
    "max_offres": 5,
    "sources": ["pole_emploi"]
}

print("🧪 Test API POST /scrape-offres")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\n✅ Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result.get('success')}")
        print(f"📊 Total offres: {result.get('results', {}).get('total_offres', 0)}")
        print(f"🔍 Offres trouvées: {len(result.get('results', {}).get('offres', []))}")
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Exception: {e}")