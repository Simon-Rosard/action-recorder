#!/usr/bin/env python3
"""
Script pour exporter une session au format JSON ou CSV
"""

import requests
import json
import csv
import sys
from datetime import datetime

BASE_URL = "http://localhost:19000/api/recording"

def export_to_json(session_data, filename):
    """Exporte une session au format JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"✅ Session exportée vers {filename}")

def export_to_csv(session_data, filename):
    """Exporte une session au format CSV."""
    if not session_data.get('actions'):
        print("❌ Aucune action à exporter")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'timestamp', 'action_type', 'x', 'y', 'button', 
            'key', 'scroll_direction', 'scroll_amount'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for action in session_data['actions']:
            row = {field: action.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"✅ Session exportée vers {filename}")

def list_sessions():
    """Liste toutes les sessions disponibles."""
    try:
        response = requests.get(f"{BASE_URL}/sessions")
        if response.status_code == 200:
            sessions = response.json()
            if not sessions:
                print("📭 Aucune session trouvée")
                return []
            
            print("📋 Sessions disponibles:")
            for i, session in enumerate(sessions, 1):
                duration = "En cours"
                if session.get('end_time'):
                    start = datetime.fromisoformat(session['start_time'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(session['end_time'].replace('Z', '+00:00'))
                    duration = f"{(end - start).total_seconds():.1f}s"
                
                print(f"  {i}. {session['name']} ({session['id'][:8]}...)")
                print(f"     📊 {len(session.get('actions', []))} actions - ⏱️ {duration}")
            
            return sessions
        else:
            print(f"❌ Erreur lors de la récupération: {response.text}")
            return []
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au service")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python export_session.py <session_id> [format] [filename]")
        print("       python export_session.py list")
        print("")
        print("Formats supportés: json, csv (défaut: json)")
        print("")
        list_sessions()
        return
    
    if sys.argv[1] == "list":
        list_sessions()
        return
    
    session_id = sys.argv[1]
    format_type = sys.argv[2] if len(sys.argv) > 2 else "json"
    filename = sys.argv[3] if len(sys.argv) > 3 else None
    
    if format_type not in ["json", "csv"]:
        print("❌ Format non supporté. Utilisez 'json' ou 'csv'")
        return
    
    # Récupérer la session
    try:
        response = requests.get(f"{BASE_URL}/sessions/{session_id}")
        if response.status_code == 404:
            print(f"❌ Session {session_id} non trouvée")
            print("\n📋 Sessions disponibles:")
            list_sessions()
            return
        elif response.status_code != 200:
            print(f"❌ Erreur lors de la récupération: {response.text}")
            return
        
        session_data = response.json()
        
        # Générer le nom de fichier si non spécifié
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = session_data.get('name', 'session').replace(' ', '_')
            filename = f"{safe_name}_{timestamp}.{format_type}"
        
        # Exporter selon le format
        if format_type == "json":
            export_to_json(session_data, filename)
        else:
            export_to_csv(session_data, filename)
        
        # Afficher un résumé
        print(f"\n📊 Résumé de l'export:")
        print(f"   Session: {session_data.get('name', 'Sans nom')}")
        print(f"   Actions: {len(session_data.get('actions', []))}")
        print(f"   Format: {format_type.upper()}")
        print(f"   Fichier: {filename}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au service")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    main()