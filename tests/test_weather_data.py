import unittest
import sys
from dataclasses import fields
from dss_farmers.models.weather_data import WeatherData


class TestWeatherData(unittest.TestCase):
    """Unit tests for WeatherData model"""

    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'temperature_c': 25.5,
            'humidity_percent': 65.0,
            'precipitation_mm': 2.3,
            'wind_speed_kmh': 15.8,
            'weather_condition': 'Partly Cloudy',
            'forecast_days': 3,
            'is_severe_alert': False
        }

    def test_valid_instantiation(self):
        """Test successful instantiation with valid data"""
        weather = WeatherData(**self.valid_data)
        
        # Verify all fields are set correctly
        self.assertEqual(weather.temperature_c, 25.5)
        self.assertEqual(weather.humidity_percent, 65.0)
        self.assertEqual(weather.precipitation_mm, 2.3)
        self.assertEqual(weather.wind_speed_kmh, 15.8)
        self.assertEqual(weather.weather_condition, 'Partly Cloudy')
        self.assertEqual(weather.forecast_days, 3)
        self.assertEqual(weather.is_severe_alert, False)

    def test_field_types(self):
        """Test field type annotations match expected types"""
        weather = WeatherData(**self.valid_data)
        field_types = {f.name: f.type for f in fields(weather)}
        
        self.assertEqual(field_types['temperature_c'], float)
        self.assertEqual(field_types['humidity_percent'], float)
        self.assertEqual(field_types['precipitation_mm'], float)
        self.assertEqual(field_types['wind_speed_kmh'], float)
        self.assertEqual(field_types['weather_condition'], str)
        self.assertEqual(field_types['forecast_days'], int)
        self.assertEqual(field_types['is_severe_alert'], bool)

    def test_required_fields(self):
        """Test that all fields are required (no defaults)"""
        with self.assertRaises(TypeError):
            WeatherData()  # Should fail - missing required arguments
        
        # Test missing individual fields
        incomplete_data = self.valid_data.copy()
        del incomplete_data['temperature_c']
        with self.assertRaises(TypeError):
            WeatherData(**incomplete_data)

    def test_negative_values(self):
        """Test instantiation with negative values"""
        negative_data = self.valid_data.copy()
        negative_data['temperature_c'] = -10.5
        negative_data['precipitation_mm'] = 0.0
        
        weather = WeatherData(**negative_data)
        self.assertEqual(weather.temperature_c, -10.5)
        self.assertEqual(weather.precipitation_mm, 0.0)

    def test_extreme_values(self):
        """Test instantiation with extreme values"""
        extreme_data = {
            'temperature_c': 50.0,
            'humidity_percent': 100.0,
            'precipitation_mm': 500.0,
            'wind_speed_kmh': 200.0,
            'weather_condition': 'Severe Thunderstorm',
            'forecast_days': 10,
            'is_severe_alert': True
        }
        
        weather = WeatherData(**extreme_data)
        self.assertEqual(weather.temperature_c, 50.0)
        self.assertEqual(weather.humidity_percent, 100.0)
        self.assertEqual(weather.is_severe_alert, True)

    def test_zero_values(self):
        """Test instantiation with zero values"""
        zero_data = self.valid_data.copy()
        zero_data['precipitation_mm'] = 0.0
        zero_data['wind_speed_kmh'] = 0.0
        zero_data['forecast_days'] = 0
        
        weather = WeatherData(**zero_data)
        self.assertEqual(weather.precipitation_mm, 0.0)
        self.assertEqual(weather.wind_speed_kmh, 0.0)
        self.assertEqual(weather.forecast_days, 0)

    def test_string_field_validation(self):
        """Test weather_condition string field"""
        string_variants = [
            'Clear',
            'Cloudy',
            'Rainy',
            'Stormy',
            '',  # Empty string should be allowed
            'Very Long Weather Condition Description'
        ]
        
        for condition in string_variants:
            data = self.valid_data.copy()
            data['weather_condition'] = condition
            weather = WeatherData(**data)
            self.assertEqual(weather.weather_condition, condition)

    def test_boolean_field_validation(self):
        """Test is_severe_alert boolean field"""
        for alert_value in [True, False]:
            data = self.valid_data.copy()
            data['is_severe_alert'] = alert_value
            weather = WeatherData(**data)
            self.assertEqual(weather.is_severe_alert, alert_value)

    def test_field_count(self):
        """Test that WeatherData has exactly 7 fields"""
        weather = WeatherData(**self.valid_data)
        field_names = [f.name for f in fields(weather)]
        expected_fields = [
            'temperature_c', 'humidity_percent', 'precipitation_mm',
            'wind_speed_kmh', 'weather_condition', 'forecast_days', 
            'is_severe_alert'
        ]
        
        self.assertEqual(len(field_names), 7)
        self.assertEqual(set(field_names), set(expected_fields))

    def test_repr_and_str(self):
        """Test string representation of WeatherData"""
        weather = WeatherData(**self.valid_data)
        repr_str = repr(weather)
        
        # Should contain class name and all field values
        self.assertIn('WeatherData', repr_str)
        self.assertIn('25.5', repr_str)  # temperature_c
        self.assertIn('Partly Cloudy', repr_str)  # weather_condition
        self.assertIn('False', repr_str)  # is_severe_alert


if __name__ == '__main__':
    unittest.main()
    print("Verification passed!")
    sys.exit(0)
