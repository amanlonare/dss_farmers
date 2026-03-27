import unittest
from dss_farmers.models.demographic_model import DemographicInfo
from dss_farmers.models.farmer_input import FarmerInput

class TestDemographicModel(unittest.TestCase):

    def test_demographic_info_initialization(self):
        demographic_info = DemographicInfo(age=30, gender='Male', location='Farmville')
        self.assertEqual(demographic_info.age, 30)
        self.assertEqual(demographic_info.gender, 'Male')
        self.assertEqual(demographic_info.location, 'Farmville')

    def test_farmer_input_integration(self):
        farmer_input = FarmerInput(name='John Doe', demographic_info=DemographicInfo(age=30, gender='Male', location='Farmville'))
        self.assertEqual(farmer_input.name, 'John Doe')
        self.assertEqual(farmer_input.demographic_info.age, 30)
        self.assertEqual(farmer_input.demographic_info.gender, 'Male')
        self.assertEqual(farmer_input.demographic_info.location, 'Farmville')

if __name__ == '__main__':
    unittest.main()
