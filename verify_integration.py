import sys
import os
import unittest
import json
from io import BytesIO

# Add python_backend to path
sys.path.append(os.path.join(os.getcwd(), 'python_backend'))

from app import app, data_store

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Reset data store
        data_store['courses'] = []
        data_store['professors'] = []
        data_store['timeslots'] = []
        
    def test_load_defaults(self):
        print("\nTesting /api/load_defaults...")
        response = self.app.post('/api/load_defaults')
        data = json.loads(response.data)
        
        if response.status_code != 200:
            print(f"Error: {data.get('error')}")
            
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data_store['professors']), 0)
        self.assertGreater(len(data_store['courses']), 0)
        print(f"Success! Loaded {len(data_store['professors'])} professors and {len(data_store['courses'])} courses.")
        
    def test_upload_excel(self):
        print("\nTesting /api/upload_excel...")
        # Reset data
        data_store['courses'] = []
        data_store['professors'] = []
        
        sample_file = 'sample_data/Horarios EneAbr18(1).xlsx'
        with open(sample_file, 'rb') as f:
            file_content = f.read()
            
        data = {
            'file': (BytesIO(file_content), 'Horarios EneAbr18(1).xlsx')
        }
        
        response = self.app.post('/api/upload_excel', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        if response.status_code != 200:
            print(f"Error: {result.get('error')}")
            
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        self.assertGreater(len(data_store['professors']), 0)
        self.assertGreater(len(data_store['courses']), 0)
        print(f"Success! Uploaded and extracted {len(data_store['professors'])} professors and {len(data_store['courses'])} courses.")

if __name__ == '__main__':
    unittest.main()
