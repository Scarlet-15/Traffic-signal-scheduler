from datetime import datetime, timedelta
from typing import Dict, List, Any
import math

class TrafficScheduler:
    def __init__(self):
        # Base weights for different vehicle types
        self.vehicle_weights = {
            'pedestrian': 1, 'people': 2, 'bicycle': 5, 'car': 20,
            'van': 50, 'truck': 100, 'bus': 100, 'motor': 10,
            'tricycle': 7, 'awning-tricycle': 8
        }
        
        # Time factors for different periods of the day
        self.time_factors = {
            'morning_rush': (6, 9, 1.5),    # 6 AM - 9 AM
            'evening_rush': (16, 19, 1.5),  # 4 PM - 7 PM
            'normal': (0, 24, 1.0)          # Default factor
        }
        
        # Minimum and maximum green light durations (seconds)
        self.MIN_DURATION = 15
        self.MAX_DURATION = 120
        
        # Historical data storage
        self.historical_data = {}

    def _get_time_factor(self, current_hour: int) -> float:
        """Determine time-based adjustment factor based on hour of day."""
        for period, (start, end, factor) in self.time_factors.items():
            if start <= current_hour < end:
                if period in ['morning_rush', 'evening_rush']:
                    return factor
        return 1.0

    def _calculate_congestion_factor(self, vehicles: Dict[str, int]) -> float:
        """Calculate congestion factor based on vehicle density."""
        total_vehicles = sum(vehicles.values())
        if total_vehicles == 0:
            return 1.0
        
        # Exponential factor based on vehicle density
        return 1.0 + math.log(total_vehicles + 1, 10) * 0.2

    def _apply_weather_adjustment(self, duration: float, weather_condition: str = 'normal') -> float:
        """Adjust timing based on weather conditions."""
        weather_factors = {
            'rain': 1.2,    # Longer duration in rain
            'snow': 1.4,    # Even longer in snow
            'fog': 1.15,    # Slightly longer in fog
            'normal': 1.0   # No adjustment
        }
        return duration * weather_factors.get(weather_condition, 1.0)

    def calculate_weighted_sum(self, 
                             input_dict: Dict[str, Dict[str, int]], 
                             weather_condition: str = 'normal') -> Dict[str, float]:
        """Calculate weighted sums with multiple adjustment factors."""
        result = {}
        current_hour = datetime.now().hour
        time_factor = self._get_time_factor(current_hour)

        for section, vehicles in input_dict.items():
            # Base weighted sum
            weighted_sum = sum(count * self.vehicle_weights[vehicle_type] 
                             for vehicle_type, count in vehicles.items())
            
            # Apply various adjustment factors
            congestion_factor = self._calculate_congestion_factor(vehicles)
            
            # Combine all factors
            adjusted_sum = weighted_sum * time_factor * congestion_factor
            
            # Apply weather adjustment
            adjusted_sum = self._apply_weather_adjustment(adjusted_sum, weather_condition)
            
            result[section] = adjusted_sum

        return result

    def _optimize_adjacent_sections(self, schedule: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Optimize timings for adjacent sections to create green waves."""
        sections = list(schedule.keys())
        for i in range(len(sections) - 1):
            current_section = sections[i]
            next_section = sections[i + 1]
            
            # Adjust timing to create green wave effect
            current_duration = datetime.strptime(schedule[current_section]['end_time'], '%Y-%m-%d %H:%M:%S') - \
                             datetime.strptime(schedule[current_section]['start_time'], '%Y-%m-%d %H:%M:%S')
            
            if current_duration.total_seconds() > self.MIN_DURATION:
                # Adjust timing to allow for vehicle progression
                schedule[next_section]['start_time'] = (
                    datetime.strptime(schedule[current_section]['start_time'], '%Y-%m-%d %H:%M:%S') + 
                    timedelta(seconds=5)
                ).strftime('%Y-%m-%d %H:%M:%S')

        return schedule

    def generate_schedule(self, 
                         weighted_sums: Dict[str, float], 
                         weather_condition: str = 'normal') -> Dict[str, Dict[str, str]]:
        """Generate optimized traffic schedule with various constraints."""
        current_time = datetime.now()
        schedule = {}
        
        # Sort sections by weighted sum
        sorted_sections = sorted(weighted_sums.items(), key=lambda x: x[1], reverse=True)

        for section, weight in sorted_sections:
            # Calculate base duration
            base_duration = weight * 0.2
            
            # Apply constraints
            duration_seconds = min(max(base_duration, self.MIN_DURATION), self.MAX_DURATION)
            
            # Create timedelta
            duration = timedelta(seconds=duration_seconds)
            end_time = current_time + duration

            schedule[section] = {
                'start_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': str(duration),
                'weight': weight
            }
            
            # Store in historical data
            self.historical_data[section] = self.historical_data.get(section, []) + [weight]
            
            current_time = end_time

        # Optimize for adjacent sections
        schedule = self._optimize_adjacent_sections(schedule)
        
        return schedule

def main():
    # Example usage
    input_data = {
        's1': {'pedestrian': 0, 'people': 0, 'bicycle': 0, 'car': 16, 'van': 3, 'truck': 0, 'bus': 0, 'motor': 0, 'tricycle': 0, 'awning-tricycle': 0},
        's2': {'pedestrian': 0, 'people': 0, 'bicycle': 0, 'car': 7, 'van': 0, 'truck': 0, 'bus': 0, 'motor': 0, 'tricycle': 0, 'awning-tricycle': 0},
        's3': {'pedestrian': 0, 'people': 0, 'bicycle': 0, 'car': 4, 'van': 0, 'truck': 0, 'bus': 0, 'motor': 0, 'tricycle': 0, 'awning-tricycle': 0}
    }

    scheduler = TrafficScheduler()
    weighted_sums = scheduler.calculate_weighted_sum(input_data, weather_condition='rain')
    schedule = scheduler.generate_schedule(weighted_sums)
    
    print("Weighted Sums:", weighted_sums)
    print("\nOptimized Schedule:")
    for section, times in schedule.items():
        print(f"{section}: {times}")

if __name__ == "__main__":
    main()