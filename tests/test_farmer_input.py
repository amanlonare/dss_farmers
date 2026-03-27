import sys
from dss_farmers.models.farmer_input import FarmerInput
from dss_farmers.models.demographic_info import DemographicInfo

def test_farmer_input():
    demographic_info = DemographicInfo(gender="Male", income_level="Medium")
    farmer_input = FarmerInput(location="Farmville", demographic=demographic_info)
    
    assert farmer_input.location == "Farmville"
    assert farmer_input.demographic.gender == "Male"
    assert farmer_input.demographic.income_level == "Medium"
    
    print("Verification passed!")
    sys.exit(0)

if __name__ == "__main__":
    test_farmer_input()
