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
        self.saved_env_admin_pass = os.environ.get('ADMIN_PASSWORD')

    def tearDown(self):
        if self.saved_env_admin_pass is not None:
            os.environ['ADMIN_PASSWORD'] = self.saved_env_admin_pass
        else:
            os.environ.pop('ADMIN_PASSWORD', None)
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
        a,b = auth.hash_password('Password@123'), auth.hash_password('Password@123')
        self.assertNotEqual(a,b)
        self.assertTrue(auth.verify_password('Password@123',a))

    def test_admin_seeding_and_secret_sync(self):
        # Initial: without password, seeding returns False
        os.environ.pop('ADMIN_PASSWORD', None)
        self.assertFalse(auth.seed_admin())
        self.assertFalse(auth.is_admin_configured())

        # Seed admin with first password
        os.environ['ADMIN_PASSWORD'] = 'InitialPass@123'
        self.assertTrue(auth.seed_admin())
        self.assertTrue(auth.is_admin_configured())
        user = auth.authenticate('admin', 'InitialPass@123')
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'admin')

        # Rotate password via environment/secrets and verify sync
        os.environ['ADMIN_PASSWORD'] = 'RotatedPass@456'
        self.assertTrue(auth.seed_admin())
        self.assertIsNone(auth.authenticate('admin', 'InitialPass@123'))
        user_new = auth.authenticate('admin', 'RotatedPass@456')
        self.assertIsNotNone(user_new)
        self.assertEqual(user_new['username'], 'admin')


if __name__ == '__main__':
    unittest.main()
