import math
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
from shapely.ops import nearest_points

from shapely import LineString, MultiPoint, Point, unary_union

RSSImax = -20
RSSImin = -90

df = pd.read_csv('wifi_networks.csv');

data = df.to_numpy()
df = pd.DataFrame(data, columns=[
    'Timestamp', 'SSID', 'BSSID', 'Signal Strength (%)', 'Signal Strength (dbm)'
    ,'Estimated Distance (m)','Latitude', 'Longitude','Device Network Status'])

df['Signal Strength (%)'] = df['Signal Strength (%)'].replace("%", "")

# calcul de l'intensité du signal avec l'approximation
df['Signal Strength_2.0'] = (df['Signal Strength (%)'].astype(float)/100) * (RSSImax - RSSImin) + RSSImin

# Estimation de la distance 
df['dist'] = round(10 ** ((27.55 - (20 * math.log10(2400)) + abs(df['Signal Strength_2.0']).astype(float)) / 20), 2)

# --------------------------------------------------
# 1) Read and prepare the data
# --------------------------------------------------

filter = (
    (data[:, 0] == "31/03/2025 10:41") 
    & (data[:, 1] == "Petit Lapin 2025") 
)

filtered_df = df[(df['Timestamp'] == "31/03/2025 10:41") & (df['SSID'] == "Isep NDL EAP")]

lat_center = float(filtered_df.iloc[0]['Latitude'])
lon_center = float(filtered_df.iloc[0]['Longitude'])
m = folium.Map(location=[lat_center, lon_center], zoom_start=17)

for _, row in filtered_df.iterrows():
    folium.Circle(
        location=(row['Latitude'], row['Longitude']),
        radius=row['dist'],  # Use the estimated distance as the radius
        popup=f"{row['SSID']} @ {row['Timestamp']} @ {row['dist']}",
        color="blue",
        fill=True,
        fill_opacity=0.3
    ).add_to(m)


# --------------------------------------------------
# 2) Filter data and remove the smallest circle
# --------------------------------------------------
filtered_df = df[(df['Timestamp'] == "31/03/2025 10:41") & (df['ssid'] == "Petit Lapin 2025")]

if len(filtered_df) < 2:
    print("Need at least 2 circles to find an intersection. Exiting.")
    exit()

# Constants
MARGIN = 2.5  # meters added to each radius for intersection calculation


def estimate_position(filtered_df):
    """Estimate position using Shapely with margin-added circles"""
    if len(filtered_df) == 0:
        return None
    if len(filtered_df) == 1:
        return (float(filtered_df.iloc[0]['Latitude']), 
                float(filtered_df.iloc[0]['Longitude']))

    valid_circles = []
    for _, row in filtered_df.iterrows():
        try:
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            dist = float(row['dist'])
            
            # Skip invalid distances
            if not np.isfinite(dist) or dist < MARGIN:
                continue
                
            point = Point(lon, lat)
            radius = dist + MARGIN
            valid_circles.append(point.buffer(radius))
        except (ValueError, TypeError):
            continue
    
    if not valid_circles:
        # Fallback if no valid circles
        avg_lat = filtered_df['Latitude'].astype(float).mean()
        avg_lon = filtered_df['Longitude'].astype(float).mean()
        return (avg_lat, avg_lon)
    
    # Find intersection of all valid circles
    intersection = unary_union(valid_circles)
    
    if intersection.is_empty:
        # No intersection - return centroid of all access points
        centers = [Point(float(row['Longitude']), float(row['Latitude'])) 
                 for _, row in filtered_df.iterrows()]
        return (MultiPoint(centers).centroid.y, MultiPoint(centers).centroid.x)
    elif intersection.geom_type == 'Point':
        # Single point intersection
        return (intersection.y, intersection.x)
    else:
        # Return centroid of intersection area
        return (intersection.centroid.y, intersection.centroid.x)




estimated_position = estimate_position(filtered_df)
if filtered_df.empty:
    print("No circles left after removing the smallest circle.")
    exit()

estimated_position = estimate_position(filtered_df)

print(estimated_position)
folium.Marker(
    location=estimated_position,
    popup=f"<b>Estimated Position</b><br>Margin: {MARGIN}m",
    icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
    tooltip="Click for details"
).add_to(m)

# Optional accuracy circle
folium.Circle(
    location=estimated_position,
    radius=MARGIN,
    color="red",
    fill=True,
    fill_opacity=0.1,
    popup=f"Estimation Accuracy: ±{MARGIN}m"
).add_to(m)
m.save("wifi_map.html")