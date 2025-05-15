from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict
import pandas as pd
from scipy import stats

class TrafficHistoricalAnalyzer:
    def __init__(self):
        self.historical_data = defaultdict(lambda: {
            'weighted_sums': [],
            'timestamps': [],
            'weather_conditions': [],
            'vehicle_counts': [],
            'wait_times': [],
            'throughput': []
        })
        
        # Define time windows for different analyses
        self.time_windows = {
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'weekly': timedelta(days=7),
            'monthly': timedelta(days=30)
        }
        
    def store_traffic_data(self, 
                          section_id: str,
                          weighted_sum: float,
                          vehicle_count: Dict[str, int],
                          weather: str,
                          wait_time: float,
                          throughput: int) -> None:
        """Store traffic data for a section with timestamp."""
        current_time = datetime.now()
         
        self.historical_data[section_id]['weighted_sums'].append(weighted_sum)
        self.historical_data[section_id]['timestamps'].append(current_time)
        self.historical_data[section_id]['weather_conditions'].append(weather)
        self.historical_data[section_id]['vehicle_counts'].append(vehicle_count)
        self.historical_data[section_id]['wait_times'].append(wait_time)
        self.historical_data[section_id]['throughput'].append(throughput)

    def get_pattern_prediction(self, 
                             section_id: str, 
                             current_time: datetime,
                             window: str = 'hourly') -> Tuple[float, float]:
        """Predict traffic pattern based on historical data."""
        if section_id not in self.historical_data:
            return None, None

        # Get relevant historical data for the time window
        historical = self.historical_data[section_id]
        time_delta = self.time_windows[window]
        
        # Filter data for similar time periods
        similar_time_indices = [
            i for i, timestamp in enumerate(historical['timestamps'])
            if (timestamp.hour == current_time.hour and
                timestamp.weekday() == current_time.weekday())
        ]
        
        if not similar_time_indices:
            return None, None

        # Calculate average and standard deviation
        relevant_sums = [historical['weighted_sums'][i] for i in similar_time_indices]
        avg_sum = np.mean(relevant_sums)
        std_dev = np.std(relevant_sums)
        
        return avg_sum, std_dev

    def analyze_trends(self, 
                      section_id: str, 
                      window: str = 'daily') -> Dict[str, Any]:
        """Analyze traffic trends for a section."""
        if section_id not in self.historical_data:
            return {}

        data = self.historical_data[section_id]
        df = pd.DataFrame({
            'timestamp': data['timestamps'],
            'weighted_sum': data['weighted_sums'],
            'wait_time': data['wait_times'],
            'throughput': data['throughput']
        })
        
        # Resample data based on window
        window_map = {'hourly': 'H', 'daily': 'D', 'weekly': 'W', 'monthly': 'M'}
        resampled = df.set_index('timestamp').resample(window_map[window]).mean()
        
        # Calculate trends
        weighted_sum_trend = stats.linregress(range(len(resampled)), resampled['weighted_sum'])
        
        return {
            'trend_slope': weighted_sum_trend.slope,
            'trend_r_value': weighted_sum_trend.rvalue,
            'mean_weighted_sum': resampled['weighted_sum'].mean(),
            'mean_wait_time': resampled['wait_time'].mean(),
            'mean_throughput': resampled['throughput'].mean()
        }

    def detect_anomalies(self, 
                        section_id: str, 
                        current_value: float,
                        z_score_threshold: float = 2.0) -> bool:
        """Detect if current traffic pattern is anomalous."""
        if section_id not in self.historical_data:
            return False

        historical_sums = self.historical_data[section_id]['weighted_sums']
        if len(historical_sums) < 10:  # Need minimum data points
            return False

        mean = np.mean(historical_sums)
        std = np.std(historical_sums)
        
        if std == 0:
            return False
            
        z_score = abs((current_value - mean) / std)
        return z_score > z_score_threshold

    def optimize_timing_with_history(self,
                                   section_id: str,
                                   current_weight: float,
                                   base_duration: float) -> float:
        """Optimize signal timing using historical patterns."""
        current_time = datetime.now()
        predicted_weight, std_dev = self.get_pattern_prediction(section_id, current_time)
        
        if predicted_weight is None:
            return base_duration
            
        # Adjust duration based on historical patterns
        if current_weight > predicted_weight + std_dev:
            # Heavier traffic than usual
            return base_duration * 1.2
        elif current_weight < predicted_weight - std_dev:
            # Lighter traffic than usual
            return base_duration * 0.8
        
        return base_duration

    def generate_traffic_report(self, 
                              section_id: str, 
                              window: str = 'daily') -> Dict[str, Any]:
        """Generate comprehensive traffic report for a section."""
        trends = self.analyze_trends(section_id, window)
        current_time = datetime.now()
        predicted_weight, std_dev = self.get_pattern_prediction(section_id, current_time)
        
        return {
            'trends': trends,
            'predicted_load': predicted_weight,
            'variation': std_dev,
            'historical_summary': {
                'peak_times': self._find_peak_times(section_id),
                'typical_patterns': self._analyze_patterns(section_id),
                'performance_metrics': self._calculate_performance_metrics(section_id)
            }
        }

    def _find_peak_times(self, section_id: str) -> Dict[str, List[int]]:
        """Identify peak traffic times."""
        data = self.historical_data[section_id]
        df = pd.DataFrame({
            'timestamp': data['timestamps'],
            'weighted_sum': data['weighted_sums']
        })
        
        # Group by hour and calculate mean
        hourly_means = df.groupby(df['timestamp'].dt.hour)['weighted_sum'].mean()
        peak_hours = hourly_means.nlargest(3).index.tolist()
        
        return {
            'peak_hours': peak_hours,
            'peak_values': hourly_means[peak_hours].tolist()
        }

    def _analyze_patterns(self, section_id: str) -> Dict[str, Any]:
        """Analyze typical traffic patterns."""
        data = self.historical_data[section_id]
        df = pd.DataFrame({
            'timestamp': data['timestamps'],
            'weighted_sum': data['weighted_sums']
        })
        
        # Analyze patterns by day of week
        daily_patterns = df.groupby(df['timestamp'].dt.dayofweek)['weighted_sum'].mean()
        
        return {
            'weekday_averages': daily_patterns.to_dict(),
            'busiest_day': daily_patterns.idxmax(),
            'quietest_day': daily_patterns.idxmin()
        }

    def _calculate_performance_metrics(self, section_id: str) -> Dict[str, float]:
        """Calculate various performance metrics."""
        data = self.historical_data[section_id]
        
        return {
            'average_wait_time': np.mean(data['wait_times']),
            'average_throughput': np.mean(data['throughput']),
            'wait_time_std': np.std(data['wait_times']),
            'throughput_std': np.std(data['throughput'])
        }

# Example usage
def main():
    analyzer = TrafficHistoricalAnalyzer()
    
    # Simulate storing some historical data
    for _ in range(100):
        analyzer.store_traffic_data(
            section_id='s1',
            weighted_sum=np.random.normal(100, 20),
            vehicle_count={'car': 10, 'truck': 2},
            weather='normal',
            wait_time=np.random.normal(30, 5),
            throughput=np.random.normal(20, 3)
        )
    
    # Generate and print report
    report = analyzer.generate_traffic_report('s1')
    print("Traffic Analysis Report:")
    print(f"Trends: {report['trends']}")
    print(f"Predicted Load: {report['predicted_load']}")
    print(f"Peak Times: {report['historical_summary']['peak_times']}")
    print(f"Performance Metrics: {report['historical_summary']['performance_metrics']}")

if __name__ == "__main__":
    main()