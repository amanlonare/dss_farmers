import sys
sys.path.append('.')

from dss_farmers.models.weather_data import WeatherData

def test_weather_data():
    sample_forecast = [
        {"day": 1, "temp": 25.5, "condition": "Sunny"},
        {"day": 2, "temp": 24.0, "condition": "Partly cloudy"}
    ]
    
    weather = WeatherData(
        temperature=23.5,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=5.2,
        pressure=1013.25,
        uv_index=7.0,
        forecast_7day=sample_forecast
    )

    assert weather.temperature == 23.5
    assert weather.humidity == 60.0
    assert weather.precipitation == 0.0
    assert weather.wind_speed == 5.2
    assert weather.pressure == 1013.25
    assert weather.uv_index == 7.0
    assert len(weather.forecast_7day) == 2
    assert weather.forecast_7day[0]["temp"] == 25.5

    print("Verification passed!")
    sys.exit(0)

if __name__ == "__main__":
    test_weather_data()
