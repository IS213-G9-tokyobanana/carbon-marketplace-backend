import unittest
import responses
from notify import retrieve_users_information
from unittest.mock import patch, MagicMock

class Test_Notify(unittest.TestCase):

    @responses.activate
    def test_retrieve_users_information(self):
        
        responses.get(
            url='http://localhost:5001/users',
            json='john@gmail.com',
            status=200
        )
        self.assertEqual(retrieve_users_information(), 'john@gmail.com')

    
if __name__ == '__main__':
    unittest.main()