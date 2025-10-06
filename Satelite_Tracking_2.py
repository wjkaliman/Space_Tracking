import requests
import os
from datetime import datetime, UTC
from skyfield.api import EarthSatellite, load, Topos
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 🔐 Credentials
USERNAME = os.getenv("SPACETRACK_USER", "wjkaliman@gmail.com")
PASSWORD = os.getenv("SPACETRACK_PASS", "Canon2025Ball2026")

# 🛰️ Satellite NORAD IDs
SAT_IDS = [25544, 43013, 39444]  # ISS, NOAA-20, etc.

# 🔄 Fetch TLE from Space-Track
def get_tle(norad_id):
    session = requests.Session()
    login_url = "https://www.space-track.org/ajaxauth/login"
    login_data = {"identity": USERNAME, "password": PASSWORD}
    session.post(login_url, data=login_data)

    tle_url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{norad_id}/orderby/ORDINAL asc/format/tle"
    response = session.get(tle_url)
    lines = response.text.strip().splitlines()
    return lines if len(lines) >= 2 else None

# 🧮 Load TLEs
def load_tle_data():
    tle_data = {}
    for sat_id in SAT_IDS:
        lines = get_tle(sat_id)
        if lines:
            tle_data[f"SAT_{sat_id}"] = lines[:2]
            print(f"Loaded TLE for SAT_{sat_id}: {lines[0]}")
        else:
            print(f"Failed to load TLE for {sat_id}")
    return tle_data

# 🌍 Plot ground tracks
def plot_ground_tracks(tle_data, ts, times):
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.set_title("Satellite Ground Tracks")

    for name, tle in tle_data.items():
        try:
            satellite = EarthSatellite(tle[0], tle[1], name, ts)
            geocentric = satellite.at(times)
            subpoint = geocentric.subpoint()
            longitudes = subpoint.longitude.degrees
            latitudes = subpoint.latitude.degrees
            ax.plot(longitudes, latitudes, label=name, transform=ccrs.Geodetic())
            print(f"{name} → Longitudes: {longitudes[:5]}")
            print(f"{name} → Latitudes: {latitudes[:5]}")
        except Exception as e:
            print(f"Error plotting {name}: {e}")

    ax.legend()
    return fig

# 📁 Save plot
def save_plot(fig, timestamp):
    output_path = f"ground_tracks_{timestamp}.png"
    fig.savefig(output_path, dpi=300)
    print(f"Ground track plot saved as {output_path}")

# 🧠 Display orbital parameters
def display_orbital_parameters(tle_data, ts):
    for name, tle in tle_data.items():
        satellite = EarthSatellite(tle[0], tle[1], name, ts)
        print(f"\n{name} Orbital Parameters:")
        print("  Inclination (deg):", round(satellite.model.inclo, 4))
        print("  Eccentricity:", round(satellite.model.ecco, 6))
        print("  Mean Motion (rev/day):", round(satellite.model.no_kozai, 6))
        print("  Approx. Altitude (km):", round(satellite.at(ts.now()).subpoint().elevation.km, 2))

# 📡 Predict passes over Rocklin
def predict_passes(tle_data, ts, now):
    rocklin = Topos(latitude_degrees=38.7907, longitude_degrees=-121.2358)
    t0 = ts.utc(now.year, now.month, now.day)
    t1 = ts.utc(now.year, now.month, now.day + 1)

    for name, tle in tle_data.items():
        satellite = EarthSatellite(tle[0], tle[1], name, ts)
        times, events = satellite.find_events(rocklin, t0, t1, altitude_degrees=10.0)

        print(f"\n{name} Passes Over Rocklin:")
        for t, event in zip(times, events):
            label = ('rise', 'culminate', 'set')[event]
            print(f"  {label} at {t.utc_strftime('%Y-%m-%d %H:%M:%S UTC')}")

# 🛰️ Live satellite location at a specific time
def plot_satellite_location(norad_id, target_dt):
    ts = load.timescale()
    t = ts.utc(target_dt.year, target_dt.month, target_dt.day,
               target_dt.hour, target_dt.minute, target_dt.second)

    lines = get_tle(norad_id)
    if not lines or len(lines) < 2:
        print(f"Failed to fetch TLE for NORAD ID {norad_id}")
        return

    satellite = EarthSatellite(lines[0], lines[1], f"SAT_{norad_id}", ts)
    subpoint = satellite.at(t).subpoint()

    lon = subpoint.longitude.degrees
    lat = subpoint.latitude.degrees
    alt = subpoint.elevation.km

    print(f"Satellite {norad_id} at {target_dt.isoformat()}:")
    print(f"  Latitude: {lat:.4f}°, Longitude: {lon:.4f}°, Altitude: {alt:.2f} km")

    fig = plt.figure(figsize=(10, 5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.set_title(f"Satellite {norad_id} Location at {target_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    ax.plot(lon, lat, marker='o', color='red', markersize=8, transform=ccrs.Geodetic())
    ax.text(lon + 3, lat, f"{norad_id}", transform=ccrs.Geodetic(), fontsize=10)
    plt.show()

# 🚀 Main execution
if __name__ == "__main__":
    ts = load.timescale()
    now = datetime.now(UTC)
    minutes = np.arange(0, 90, 1)
    times = ts.utc(now.year, now.month, now.day, now.hour, minutes)

    tle_data = load_tle_data()
    fig = plot_ground_tracks(tle_data, ts, times)
    save_plot(fig, now.strftime("%Y%m%d_%H%M%S"))
    display_orbital_parameters(tle_data, ts)
    predict_passes(tle_data, ts, now)

    # 🔭 Example: Live location of NOAA-20 (SAT_43013) right now
    plot_satellite_location(43013, now)