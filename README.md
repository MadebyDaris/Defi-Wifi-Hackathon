# Défi WiFi Hackathon
Projet développé durant un hackathon dont l’objectif était de localiser des points d’accès WiFi en temps réel grâce à :
- du sniffing réseau,
- une estimation de distance via la puissance du signal,
- une visualisation sur carte dans une application Flutter, et l’intégration d’un backend Python connecté à Firebase Firestore.

### 1. Sniffing WiFi – scanner.py
Le script scanner.py utilise la librairie iwlist (Linux) ou d'autres utilitaires pour détecter les points d’accès WiFi aux alentours.

```json
{
  "SSID": "Freebox-D4E",
  "BSSID": "58:ef:68:cd:d4:ef",
  "signal_dBm": -61,
  "signal_percent": 57,
  "latitude": 48.8566,
  "longitude": 2.3522,
  "timestamp": "2025-04-06T14:34:21"
}
```
Ces données sont :

Sauvegardées localement (wifi_scan.csv)

Envoyées à Firestore via une requête POST à l'API Flask (server.py).

### 2. Backend Flask – main.py
Initialement on a implementé un mini API
```
GET /scan
📡 Cela déclenche un scan puis :
```
Et puis pour simplifier le fonctionnement de l'application flutter on a utilisé FireBase pour la base de données

### 3. Parsing & estimation des distances – parser.py
Le script lit les données WiFi collectées, applique des filtres, et calcule une distance estimée à l’émetteur.

Formule mathématique utilisée
Nous utilisons le modèle FSPL (Free Space Path Loss) :
Avec :

𝑃em ≈ 23dBm
𝑃rec : signal mesuré (ex: -65 dBm)
f=2400 MHz (WiFi 2.4 GHz)
$d=10^{(Pem − Prec​ + 27.55−20⋅log(10))/20}$

### 4. Visualisation Flutter
L’application Flutter est conçue pour :

Afficher les points WiFi détectés sur une carte (flutter_map)

Tracer des cercles proportionnels à la distance estimée

Réagir en temps réel grâce à l’architecture BLoC

### 6. Firebase Firestore
