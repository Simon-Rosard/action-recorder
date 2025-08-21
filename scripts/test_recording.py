#!/usr/bin/env python3
"""
Script de test pour l'Action Recorder
"""

import requests
import time
import json

BASE_URL = "http://localhost:19000/api/recording"

def test_recording_flow():
    print("🧪 Test complet d'Action Recorder")
    print("=" * 50)
    
    # 1. Vérifier le statut
    print("1. Vérification du statut...")
    response = requests.get(f"{BASE_URL}/status")
    if response.status_code == 200:
        print(f"   ✅ Service actif: {response.json()}")
    else:
        print(f"   ❌ Service non disponible: {response.status_code}")
        return
    
    # 2. Démarrer un enregistrement
    print("\n2. Démarrage de l'enregistrement...")
    start_data = {
        "name": "Test Session",
        "config": {
            "record_mouse_moves": True,
            "record_clicks": True,
            "record_keyboard": True,
            "record_scrolling": True,
            "mouse_move_threshold": 10
        }
    }
    
    response = requests.post(f"{BASE_URL}/start", json=start_data)
    if response.status_code == 200:
        session_id = response.json()["session_id"]
        print(f"   ✅ Enregistrement démarré: {session_id}")
    else:
        print(f"   ❌ Erreur lors du démarrage: {response.text}")
        return
    
    # 3. Attendre quelques secondes pour capturer des actions
    print("\n3. Enregistrement en cours...")
    print("   📝 Effectuez quelques actions (clics, mouvements, frappes)...")
    for i in range(10, 0, -1):
        print(f"   ⏰ {i} secondes restantes", end="\r")
        time.sleep(1)
    print("\n")
    
    # 4. Arrêter l'enregistrement
    print("4. Arrêt de l'enregistrement...")
    response = requests.post(f"{BASE_URL}/stop")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Enregistrement arrêté: {result['total_actions']} actions")
    else:
        print(f"   ❌ Erreur lors de l'arrêt: {response.text}")
        return
    
    # 5. Récupérer les sessions
    print("\n5. Récupération des sessions...")
    response = requests.get(f"{BASE_URL}/sessions")
    if response.status_code == 200:
        sessions = response.json()
        print(f"   ✅ {len(sessions)} session(s) trouvée(s)")
        for session in sessions:
            print(f"   📁 {session['name']}: {len(session['actions'])} actions")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # 6. Récupérer les détails de la session
    print("\n6. Détails de la session...")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}")
    if response.status_code == 200:
        session = response.json()
        print(f"   ✅ Session '{session['name']}':")
        print(f"   📊 Actions: {len(session['actions'])}")
        print(f"   ⏱️  Durée: {session['start_time']} → {session['end_time']}")
        
        # Afficher quelques actions
        if session['actions']:
            print("   🎬 Premières actions:")
            for i, action in enumerate(session['actions'][:3]):
                print(f"      {i+1}. {action['action_type']} à {action['timestamp']}")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # 7. Test de lecture (optionnel)
    if len(session['actions']) > 0:
        print("\n7. Test de lecture...")
        print("   ⚠️  La lecture va commencer dans 3 secondes...")
        time.sleep(3)
        
        playback_data = {
            "session_id": session_id,
            "speed_multiplier": 2.0,  # Lecture 2x plus rapide
            "start_from_action": 0,
            "end_at_action": min(5, len(session['actions']))  # Max 5 actions
        }
        
        response = requests.post(f"{BASE_URL}/playback", json=playback_data)
        if response.status_code == 200:
            print("   ✅ Lecture démarrée")
            time.sleep(3)  # Laisser le temps à la lecture
        else:
            print(f"   ❌ Erreur lors de la lecture: {response.text}")
    
    print("\n🎉 Test terminé avec succès !")

if __name__ == "__main__":
    try:
        test_recording_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au service")
        print("   Assurez-vous que le service est démarré sur http://localhost:19000")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")