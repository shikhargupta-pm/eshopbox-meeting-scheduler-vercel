import unittest
import json
import os
from app import app
import database

class TestMeetingScheduler(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Ensure we use a clean SQLite DB for testing
        if os.path.exists('bookings.db'):
            os.remove('bookings.db')
        database.init_db()
        from app import LST_TEAM, FST_TEAM
        database.initialize_team_members(LST_TEAM, "LST")
        database.initialize_team_members(FST_TEAM, "FST")

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Eshopbox Experts - Demo Scheduler', response.data)

    def test_create_event_lst_volume(self):
        payload = {
            "date": "2024-01-01",
            "time_slot": "10:00",
            "volume": "1000",
            "service": "Fulfil",
            "exclude": ""
        }
        response = self.app.post('/eshopbox_create_event', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['team'], 'LST')
        self.assertIsNotNone(data['name'])

    def test_create_event_fst_volume(self):
        payload = {
            "date": "2024-01-01",
            "time_slot": "10:00",
            "volume": "5000",
            "service": "Fulfil",
            "exclude": ""
        }
        response = self.app.post('/eshopbox_create_event', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['team'], 'FST')

    def test_create_event_ship_service(self):
        payload = {
            "date": "2024-01-01",
            "time_slot": "10:00",
            "volume": "5000", # High volume but Ship service
            "service": "Ship",
            "exclude": ""
        }
        response = self.app.post('/eshopbox_create_event', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['team'], 'LST')

    def test_create_event_eshopbox_plus_service(self):
        payload = {
            "date": "2024-01-01",
            "time_slot": "10:00",
            "volume": "100", # Low volume but Plus service
            "service": "Eshopbox Plus",
            "exclude": ""
        }
        response = self.app.post('/eshopbox_create_event', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['team'], 'FST')

    def test_confirm_booking(self):
        payload = {
            "name": "Test AE",
            "email": "test@example.com",
            "date": "2024-01-01",
            "time_slot": "10:00",
            "volume": 1000,
            "service": "Test",
            "team": "TEST"
        }
        response = self.app.post('/confirm_booking',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

if __name__ == '__main__':
    unittest.main()
