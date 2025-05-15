from datetime import datetime, timedelta

def calculate_weighted_sum(input_dict):
    vehicle_weights = {
        'pedestrian': 1, 'people': 2, 'bicycle': 5, 'car': 20,
        'van': 50, 'truck': 100, 'bus': 100, 'motor': 10,
        'tricycle': 7, 'awning-tricycle': 8
    }

    result = {}
    for section, vehicles in input_dict.items():
        weighted_sum = sum(count * vehicle_weights[vehicle_type] for vehicle_type, count in vehicles.items())
        result[section] = weighted_sum

    return result

def generate_vehicle_schedule(weighted_sums):
    current_time = datetime.now()
    schedule = {}
    sorted_sections = sorted(weighted_sums.items(), key=lambda x: x[1], reverse=True)

    for section, weight in sorted_sections:
        duration = timedelta(seconds=weight * 0.2)
        end_time = current_time + duration
        schedule[section] = {
            'start_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': str(duration)
        }
        current_time = end_time

    return schedule

# Example input data
input_data = {
    's1': {'pedestrian': 0, 'people': 0, 'bicycle': 0, 'car': 16, 'van': 3, 'truck': 0, 'bus': 0, 'motor': 0, 'tricycle': 0, 'awning-tricycle': 0},
    's2': {'pedestrian': 0, 'people': 0, 'bicycle': 0, 'car': 7, 'van': 0, 'truck': 0, 'bus': 0, 'motor': 0, 'tricycle': 0, 'awning-tricycle': 0},
    's3': {'pedestrian': 0, 'people': 0, 'bicycle': 0, 'car': 4, 'van': 0, 'truck': 0, 'bus': 0, 'motor': 0, 'tricycle': 0, 'awning-tricycle': 0}
}

# Step 1: Calculate weighted sums
weighted_sums = calculate_weighted_sum(input_data)
print("Weighted Sums:")
print(weighted_sums)

# Step 2: Generate schedule
schedule = generate_vehicle_schedule(weighted_sums)
print("\nSchedule:")
for section, times in schedule.items():
    print(f"{section}: {times}")