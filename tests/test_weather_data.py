from dss_farmers.models.weather_data import WeatherData

def test_weather_data_instantiation():
    weather = WeatherData()
    assert isinstance(weather, WeatherData)
    print("WeatherData instantiation test passed!")

def test_weather_data_defaults():
    weather = WeatherData()
    assert weather.temperature == 0.0
    assert weather.humidity == 0.0
    assert weather.precipitation == 0.0
    assert weather.wind_speed == 0.0
    assert weather.pressure == 0.0
    assert weather.uv_index == 0.0
    assert weather.forecast_7day == []
    print("WeatherData default values test passed!")

def test_weather_data_custom_values():
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
    print("WeatherData custom values test passed!")

if __name__ == "__main__":
    test_weather_data_instantiation()
    test_weather_data_defaults()
    test_weather_data_custom_values()
    print("All tests passed!")
