from datetime import datetime
from flask import Flask, jsonify

import firebase_admin
from firebase_admin import credentials, db, firestore
import Scanner

def initialize_firebase():
    try:
        cred = credentials.Certificate("hackathon-defiwifi-firebase.json")
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully!")
    except ValueError:
        print(f"Firebase already initialized")
        pass


# FIREBASE APP INIT
initialize_firebase()
db = firestore.client()

app = Flask(__name__)

@app.route("/scan", methods=["GET"])
def scan_endpoint():
    data = Scanner.scan_with_metadata() 
    if data:
        Scanner.save_to_csv(data)
        save_to_firebase(data)
    return jsonify(data)

def save_to_firebase(networks):
    """Save Wi-Fi networks to Firestore with proper structure"""
    batch = db.batch()  # Use batch for better performance
    collection_ref = db.collection("wifi_scans")
    
    for network in networks:
        try:
            # Create a document reference with auto-generated ID
            doc_ref = collection_ref.document()
            
            # Prepare the data structure
            data = {
                "timestamp": datetime.now().isoformat(),
                "ssid": network.get("SSID", "Hidden Network"),
                "bssid": network.get("BSSID", ""),
                "signal": {
                    "dBm": network.get("Signal Strength (dBm)", 0),
                    "percent": network.get("Signal Strength (%)", 0)
                },
                "location": {
                    "latitude": network.get("Latitude", 0),
                    "longitude": network.get("Longitude", 0)
                },
                "metadata": {
                    "source": "python_wifi_scanner",
                    "version": "1.0"
                }
            }
            
            # Add to batch
            batch.set(doc_ref, data)
            
        except Exception as e:
            print(f"Error preparing network {network.get('SSID')}: {str(e)}")
    
    try:
        # Commit all writes at once
        batch.commit()
        print(f"Successfully saved {len(networks)} networks to Firestore")
    except Exception as e:
        print(f"Failed to save batch: {str(e)}")

def run_scanner():
    """Run scanner and save to Firebase"""
    networks = Scanner.scan_with_metadata()
    if networks:
        print(f"Found {len(networks)} networks")
        save_to_firebase(networks)
    else:
        print("No networks found to save")

if __name__ == "__main__":
    # Run scanner immediately
    run_scanner()
    
    # Start web server with scan endpoint
    app.run(debug=True)