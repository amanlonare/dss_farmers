import unittest
from dss_farmers.models.weather_details import WeatherDetails

class TestWeatherDetails(unittest.TestCase):

    def setUp(self):
        self.weather_details = WeatherDetails(
            temperature=25.0,
            humidity=60,
            wind_speed=5.0,
            description="Clear sky"
        )

    def test_initialization(self):
        self.assertEqual(self.weather_details.temperature, 25.0)
        self.assertEqual(self.weather_details.humidity, 60)
        self.assertEqual(self.weather_details.wind_speed, 5.0)
        self.assertEqual(self.weather_details.description, "Clear sky")

    def test_repr(self):
        expected_repr = (
            "WeatherDetails(temperature=25.0, humidity=60, "
            "wind_speed=5.0, description='Clear sky')"
        )
        self.assertEqual(repr(self.weather_details), expected_repr)

if __name__ == '__main__':
    unittest.main()
