import subprocess
import csv
import geocoder
import math
from datetime import datetime

def get_location():
    g = geocoder.ip('me')
    return g.latlng if g.latlng else [None, None]

def estimate_distance(dbm, freq_mhz=2400):
    # Free-space path loss formula approximation
    try:
        return round(10 ** ((27.55 - (20 * math.log10(freq_mhz)) + abs(dbm)) / 20), 2)
    except Exception:
        return None

RSSImax = -20
RSSImin = -90


def signal_percent_to_dbm(signal_percent):

    return (signal_percent / 100) * (RSSImax - RSSImin) + RSSImin

def parse_wifi_data(data):
    networks = []
    lines = data.splitlines()
    network_info = {}

    for line in lines:
        if "SSID" in line and "BSSID" not in line:
            if network_info:
                networks.append(network_info)
            network_info = {"SSID": line.split(":", 1)[1].strip()}

        elif "BSSID" in line:
            network_info["BSSID"] = line.split(":", 1)[1].strip()

        elif "Signal" in line and "%" in line:
            try:
                signal_percent = int(line.split(":", 1)[1].strip().replace('%', ''))
                dbm = signal_percent_to_dbm(signal_percent)
                distance = estimate_distance(dbm)

                network_info["Signal Strength (%)"] = signal_percent
                network_info["Signal Strength (dBm)"] = dbm
                network_info["Estimated Distance (m)"] = distance
            except ValueError:
                pass

    if network_info:
        networks.append(network_info)

    return networks

def scan_wifi():
    command = "netsh wlan show networks mode=Bssid"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        return parse_wifi_data(result.stdout)
    else:
        print("Failed to scan for networks.")
        return []

def get_connected_ssid():
    try:
        result = subprocess.run("netsh wlan show interfaces", capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":", 1)[1].strip()
    except Exception as e:
        print("Error getting connected SSID:", e)
    return None

def is_hotspot_enabled():
    try:
        result = subprocess.run("netsh wlan show hostednetwork", capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return "Status" in result.stdout and "Started" in result.stdout
    except Exception as e:
        print("Error checking hotspot status:", e)
    return False

def save_to_csv(networks, filename="wifi_networks.csv"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latitude, longitude = get_location()
    connected_ssid = get_connected_ssid()
    hotspot_active = is_hotspot_enabled()

    with open(filename, mode="a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "Timestamp", "SSID", "BSSID", "Signal Strength (%)",
            "Signal Strength (dBm)", "Estimated Distance (m)",
            "Latitude", "Longitude", "Device Network Status"
        ])

        file.seek(0, 2)
        if file.tell() == 0:
            writer.writeheader()

        for network in networks:
            ssid = network.get("SSID")
            if hotspot_active and ssid == connected_ssid:
                status = "Hotspot Active & Connected"
            elif hotspot_active:
                status = "Hotspot Active"
            elif ssid == connected_ssid:
                status = "Connected"
            else:
                status = "Not Connected"

            writer.writerow({
                "Timestamp": timestamp,
                "SSID": ssid,
                "BSSID": network.get("BSSID"),
                "Signal Strength (%)": network.get("Signal Strength (%)"),
                "Signal Strength (dBm)": network.get("Signal Strength (dBm)"),
                "Estimated Distance (m)": network.get("Estimated Distance (m)"),
                "Latitude": latitude,
                "Longitude": longitude,
                "Device Network Status": status
            })
        print(f"Data saved to {filename}")

if __name__ == "__main__":
    networks = scan_wifi()
    if networks:
        save_to_csv(networks)
    else:
        print("No Wi-Fi networks found.")
