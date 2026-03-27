import unittest
from dss_farmers.models.demographic_info import DemographicInfo
from dss_farmers.models.farmer_input import FarmerInput

class TestDemographicInfo(unittest.TestCase):
    def test_demographic_info_creation(self):
        demographic = DemographicInfo(age=30, gender='Male', education='Bachelor')
        self.assertEqual(demographic.age, 30)
        self.assertEqual(demographic.gender, 'Male')
        self.assertEqual(demographic.education, 'Bachelor')

class TestFarmerInput(unittest.TestCase):
    def test_farmer_input_creation(self):
        farmer_input = FarmerInput(name='John Doe', location='Farmville', crop='Wheat')
        self.assertEqual(farmer_input.name, 'John Doe')
        self.assertEqual(farmer_input.location, 'Farmville')
        self.assertEqual(farmer_input.crop, 'Wheat')

if __name__ == '__main__':
    unittest.main()
