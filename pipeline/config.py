"""All thresholds and tunable constants for the data pipeline live here."""

TIMEZONE = "Asia/Kuala_Lumpur"

# --- Sun / heat (sun.py) ---
FACADE_DIRECTIONS = ["N", "E", "S", "W"]
SUN_HOURS_START = 7
SUN_HOURS_END = 19
HEAT_RATING_THRESHOLDS = {  # west-facade sun hours after 2pm
    "Low": 2.0,
    "Moderate": 3.5,
    # >= Moderate threshold -> "High"
}

# --- Noise (noise.py) ---
ROAD_BASE_DB = {
    "motorway": 75,
    "trunk": 75,
    "primary": 68,
    "secondary": 64,
    "tertiary": 60,
    "residential": 55,
}
REFERENCE_DISTANCE_M = 10
BARRIER_ATTENUATION_DB = 7
TRAFFIC_PROFILE = {  # multiplier added to base dB by hour-of-day bucket
    "peak": 3,      # 07-09, 17-20
    "normal": 0,
    "quiet": -5,    # 23-05
}
NOISE_RATING_THRESHOLDS = {
    "Quiet": 55,
    "Moderate": 65,
    # >= Moderate threshold -> "Noisy"
}

# --- Flood (flood.py) ---
RELATIVE_ELEVATION_RADIUS_M = 300
FLOOD_RATING_THRESHOLDS = {
    "Low": {"min_relative_elevation_m": 1.5, "min_waterway_dist_m": 200},
    "Medium": {"min_relative_elevation_m": 0.5, "min_waterway_dist_m": 50},
    # below Medium thresholds -> "High"
}

# --- Commute (commute.py) ---
COMMUTE_DEPARTURE_AM = "08:00"
COMMUTE_DEPARTURE_PM = "18:00"
DEFAULT_DESTINATIONS = ["KL Sentral", "Putrajaya", "KLIA", "Cyberjaya", "UPM"]

# --- Amenities (amenities.py) ---
AMENITY_SEARCH_RADIUS_M = 2000
WALK_SPEED_M_PER_MIN = 80
AMENITY_TYPES = ["school", "clinic", "mosque", "supermarket", "park"]
