import pandas as pd
import numpy as np
from datetime import datetime

import matplotlib.pyplot as plt
from geopy.distance import distance as geopy_distance
import numpy as np
import folium
from geopy.distance import distance as geopy_distance

from scipy.optimize import minimize
from geopy.distance import geodesic

def estimate_emitter_location(sensor_coords, distances):
    """
    Estimate emitter position based on sensor positions and distances (radii).
    
    Args:
        sensor_coords (list of (lat, lon)): Locations of the sensors.
        distances (list of float): Corresponding distances to emitter.

    Returns:
        (lat, lon): Estimated position of emitter.
    """

    # Initial guess: average of sensor locations
    lat0 = np.mean([lat for lat, lon in sensor_coords])
    lon0 = np.mean([lon for lat, lon in sensor_coords])

    def cost_fn(x):
        est_lat, est_lon = x
        total_error = 0
        for (lat, lon), dist in zip(sensor_coords, distances):
            actual_dist = geodesic((est_lat, est_lon), (lat, lon)).meters
            total_error += (actual_dist - dist) ** 2
        return total_error

    # Run minimization
    result = minimize(cost_fn, x0=(lat0, lon0), method='L-BFGS-B')
    return result.x if result.success else (None, None)


def plot_multiple_locations_with_radii(locations):
    """
    Plot multiple points and their radius circles on a single figure.
    
    Args:
        locations (np.ndarray): A 2D numpy array of shape (N, 3), 
                                where each row is [latitude, longitude, radius_in_meters].
    """
    plt.figure(figsize=(10, 10))

    for i, (lat, lon, radius_meters) in enumerate(locations):
        angles = np.linspace(0, 360, 360)
        circle_lats = []
        circle_lons = []

        for angle in angles:
            destination = geopy_distance(meters=radius_meters).destination((lat, lon), bearing=angle)
            circle_lats.append(destination.latitude)
            circle_lons.append(destination.longitude)

        # Plot the circle
        plt.plot(circle_lons, circle_lats, label=f'Point {i+1} - {int(radius_meters)} m')
        # Plot the center
        plt.plot(lon, lat, 'ro')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Points with Radius Circles')
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    plt.show()


# Read CSV with semicolon delimiter
df = pd.read_csv('Fichier_Scan_WiFi.csv', delimiter=';')

# calcul de l'intensité du signal avec l'approximation
df['Signal Strength_2.0'] = (df['Signal Strength (%)']/100) * (RSSImax - RSSImin) + RSSImin


# Estimation de la distance 
df['Estimated Distance 2.0 (m)'] = round(10 ** ((27.55 - (20 * math.log10(2400)) + abs(df['Signal Strength_2.0'])) / 20), 2)


# Convert to a 2D NumPy array
data = df.to_numpy()

for i in range(data.shape[0]):
    if isinstance(data[i,3], str):
        prc = int(data[i,3].strip('%')) / 100
        data[i,-3]=prc * 70 - 90

# Extract received power values and convert to float
P_recue = data[:, -3].astype(float)

# Assume constant emitted power
P_emis = 23.0

# Attenuation
Att = P_emis - P_recue

# Distance calculation (in meters)
# dist = 10**((Att + 27.55 - 20 * np.log10(2.4 * 10**3)) / 20)

# data = np.concatenate((data, dist.reshape(-1,1)), axis=1)

df = pd.DataFrame(data, columns=[
    'timestamp', 'ssid', 'mac', 'signal_percent', 'signal_dbm',
    'latitude', 'longitude', 'dist'
])

df = df[df['signal_percent'].notna()]

# Convert numeric columns to proper float type
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)
df['dist'] = df['dist'].astype(float)

# Group by (timestamp, mac, latitude, longitude), and compute the average 'dist'
# df['dist'] = df.groupby(['timestamp', 'mac', 'latitude', 'longitude'])['dist'].transform('mean')

df = df.drop_duplicates(subset=['timestamp', 'mac', 'latitude', 'longitude'])

# Convert back to NumPy array (if needed)
data_updated = df.to_numpy()

# Convert to a 2D NumPy array
data = df.to_numpy()


# Extract unique sensor pairs (last two columns)
sensors = list(set([tuple(row) for row in data[:, -3:-1]]))

# Extract the time steps 
timesteps = list(set([row for row in data[:, 0]]))

timesteps = sorted(timesteps, key=lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M"))

filter = (
    (data[:, 0] == "31/03/2025 10:41") &
    (data[:, 1] == "Petit Lapin 2025") 
)

filtered_data = data[filter]

lat_center = float(filtered_data[0][-3])
lon_center = float(filtered_data[0][-2])

RSSImax = -20
RSSImin = -90


# calcul de l'intensité du signal avec l'approximation
df['signal_percent'] = df['signal_percent'].str.replace("%", "")
df['dist'] = (df['signal_percent'].astype(float)/100) * (RSSImax - RSSImin) + RSSImin
# Estimation de la distance 
# df['Estimated Distance 2.0 (m)'] = round(10 ** ((27.55 - (20 * math.log10(2400)) + abs(df['Signal Strength_2.0'])) / 20), 2)

m = folium.Map(location=[lat_center, lon_center], zoom_start=17)

a = np.concatenate((data[filter][:, :3],df['dist']), axis=1)
print(data[filter])

for row in filtered_data:
    lat = float(row[-3])
    lon = float(row[-2])
    dist = float(row[-1])  # e.g. used as radius in meters
    ssid = row[1]
    timestamp = row[0]
    
    folium.Circle(
        location=(lat, lon),
        radius=dist,  # use 'dist' as coverage
        popup=f"{ssid} @ {timestamp}",
        color="blue",
        fill=True,
        fill_opacity=0.3
    ).add_to(m)

# Save or display the map
m.save("wifi_map.html")