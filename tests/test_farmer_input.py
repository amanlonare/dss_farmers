import sys
from dss_farmers.models.farmer_input import FarmerInput
from dss_farmers.models.weather_data import WeatherData

def test_farmer_input():
    farmer_input = FarmerInput(location="Test Location")
    
    # Verify that weather_data is an instance of WeatherData
    assert isinstance(farmer_input.weather_data, WeatherData), "weather_data should be an instance of WeatherData"
    
    # Verify that a new WeatherData instance is created for each FarmerInput
    another_farmer_input = FarmerInput(location="Another Location")
    assert farmer_input.weather_data is not another_farmer_input.weather_data, "Each FarmerInput should have a unique WeatherData instance"

    print("Verification passed!")
    sys.exit(0)

if __name__ == "__main__":
    test_farmer_input()
