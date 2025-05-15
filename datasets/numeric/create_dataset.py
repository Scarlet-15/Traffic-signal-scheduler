import pandas as pd
import random

# Define constants
weather_factors = {
    'clear': 1.0,
    'rain': 1.25,
    'snow': 1.4,
    'fog': 1.15
}

time_correction_factors = {
    ('day', 'none', 'dry'): 1.00,
    ('day', 'none', 'moist_or_wet'): 0.95,
    ('day', 'none', 'wet_or_slippery'): 0.91,
    ('night', 'none', 'dry'): 0.96,
    ('night', 'none', 'moist_or_wet'): 0.92,
    ('night', 'none', 'wet_or_slippery'): 0.81,
    ('dawn', 'none', 'dry'): 0.97,
    ('dusk', 'none', 'dry'): 0.97
}

vehicle_factors = {
    'bike': 0.8,
    'car': 1.0,
    'bus': 1.2
}

# Generate synthetic dataset
data = []

for _ in range(1000):  # Generate 1000 samples
    vehicle = random.choice(['bike', 'car', 'bus'])
    duration_of_day = random.choice(['day', 'night', 'dawn', 'dusk'])
    weather = random.choice(['clear', 'rain', 'snow', 'fog'])
    
    # Set precipitation and road condition based on weather
    precipitation = 'none' if weather == 'clear' else weather
    road_condition = 'dry' if weather == 'clear' else 'moist_or_wet' if weather == 'rain' else 'wet_or_slippery'

    # Get multipliers
    wi = weather_factors[weather]
    vi = vehicle_factors[vehicle]
    ti = time_correction_factors.get((duration_of_day, 'none', road_condition), 1.0)

    # Count of vehicles of the same type
    count_of_vehicles = random.randint(1, 50)

    data.append([vehicle, duration_of_day, weather, count_of_vehicles, wi, vi, ti])

# Create DataFrame
df = pd.DataFrame(data, columns=['class_of_vehicle', 'duration_of_day', 'weather_type', 'count_of_vehicles', 'wi', 'vi', 'ti'])

# Show the first few rows
print(df.head())

# Save to CSV (optional)
df.to_csv('synthetic_vehicle_data.csv', index=False)
