import os
import tempfile
import unittest
from pathlib import Path

with tempfile.TemporaryDirectory() as ignored:
    pass

import database
import auth


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.temp.name) / 'test.db'
        database.init_db()

    def tearDown(self):
        import gc
        gc.collect()
        self.temp.cleanup()

    def test_registration_authentication(self):
        uid = auth.register_student('student_01','Student One','student@example.com','Password@123')
        self.assertGreater(uid, 0)
        self.assertEqual(auth.authenticate('student_01','Password@123')['role'],'student')
        self.assertIsNone(auth.authenticate('student_01','wrong'))
        with self.assertRaises(ValueError):
            auth.register_student('student_01','Student One','again@example.com','Password@123')

    def test_feedback_access_and_stats(self):
        uid = auth.register_student('student_02','Student Two','second@example.com','Password@123')
        faculty_id = database.list_faculty()[0]['id']
        feedback_id = database.submit_feedback(uid, faculty_id, 'DBMS', 5, 'Great class')
        self.assertGreater(feedback_id,0)
        self.assertEqual(len(database.fetch_feedback(student_id=uid)),1)
        self.assertEqual(database.dashboard_stats()['average_rating'],5)
        database.set_faculty_active(faculty_id, False)
        with self.assertRaises(ValueError):
            database.submit_feedback(uid, faculty_id, 'DBMS', 5, 'Second entry')

    def test_password_salts(self):
        a,b=auth.hash_password('Password@123'),auth.hash_password('Password@123')
        self.assertNotEqual(a,b)
        self.assertTrue(auth.verify_password('Password@123',a))

if __name__ == '__main__':
    unittest.main()
