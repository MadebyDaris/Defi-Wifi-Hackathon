import subprocess
import csv
import time
import geocoder
from datetime import datetime

def get_location():
    # Get the current location (Latitude, Longitude) of the device using geocoder
    g = geocoder.ip('me')
    return g.latlng if g.latlng else [None, None]

def parse_wifi_data(data):
    """
    Parse the output of the netsh wlan show networks command to extract SSID, BSSID, Signal Strength (dBm), and Signal Strength (%).
    """
    networks = []
    lines = data.splitlines()
    network_info = {}

    for line in lines:
        # Extract SSID
        if "SSID" in line and "BSSID" not in line:
            if network_info:  # Save the previous network before starting a new one
                networks.append(network_info)
            network_info = {"SSID": line.split(":")[1].strip()}
        
        # Extract BSSID
        elif "BSSID" in line:
            network_info["BSSID"] = line.split(":", 1)[1].strip()
        
        # Extract Signal Strength (dBm)
        elif "Signal" in line and "dBm" in line:
            # Look for 'Signal' and extract the signal strength correctly
            parts = line.split(":")
            if len(parts) > 1:
                try:
                    signal_strength_dBm = int(parts[1].strip().replace("dBm", "").strip())
                    network_info["Signal Strength (dBm)"] = signal_strength_dBm
                    # Calculate the Signal Strength as a percentage
                    signal_strength_percent = max(0, min(100, 100 + signal_strength_dBm))
                    network_info["Signal Strength (%)"] = signal_strength_percent
                except ValueError:
                    pass

    if network_info:  # Add the last network info
        networks.append(network_info)
    
    return networks

def scan_wifi():
    # Run the command to scan for networks
    command = "netsh wlan show networks mode=Bssid"
    
    # Get the output of the command
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    
    # Check if the command ran successfully
    if result.returncode == 0:
        networks = result.stdout
        return parse_wifi_data(networks)
    else:
        print("Failed to scan for networks.")
        return []

def save_to_csv(networks, filename="wifi_networks.csv"):
    # Get the current timestamp and location
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latitude, longitude = get_location()

    # Create or open the CSV file in write mode
    with open(filename, mode="a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Timestamp", "SSID", "BSSID", "Signal Strength (dBm)", "Signal Strength (%)", "Latitude", "Longitude"])
        
        # Write header if the file is empty
        file.seek(0, 2)  # Move cursor to the end of the file
        if file.tell() == 0:
            writer.writeheader()

        # Write network data to the CSV file
        for network in networks:
            network_data = {
                "Timestamp": timestamp,
                "SSID": network.get("SSID"),
                "BSSID": network.get("BSSID"),
                "Signal Strength (dBm)": network.get("Signal Strength (dBm)"),
                "Signal Strength (%)": network.get("Signal Strength (%)"),
                "Latitude": latitude,
                "Longitude": longitude
            }
            writer.writerow(network_data)
        print(f"Data saved to {filename}")

if __name__ == "__main__":
    networks = scan_wifi()
    if networks:
        save_to_csv(networks)
    else:
        print("No Wi-Fi networks found.")
