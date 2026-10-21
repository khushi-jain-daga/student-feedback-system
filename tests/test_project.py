import os
import tempfile
import unittest
from pathlib import Path

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

    def test_registration_and_authentication(self):
        # Register a regular user with registration number
        uid = auth.register_user(
            name="Alice Smith",
            username="alicesmith",
            email="alice@example.com",
            password="Password@123",
            registration_no="23BCON9999"
        )
        self.assertGreater(uid, 0)

        # Authenticate by username
        user_by_name = auth.authenticate("alicesmith", "Password@123")
        self.assertIsNotNone(user_by_name)
        self.assertEqual(user_by_name['role'], 'user')
        self.assertEqual(user_by_name['name'], 'Alice Smith')
        self.assertEqual(user_by_name['registration_no'], '23BCON9999')

        # Authenticate by email
        user_by_email = auth.authenticate("alice@example.com", "Password@123")
        self.assertIsNotNone(user_by_email)
        self.assertEqual(user_by_email['id'], uid)

        # Reject incorrect password
        self.assertIsNone(auth.authenticate("alicesmith", "WrongPassword"))

        # Reject duplicate username
        with self.assertRaises(ValueError):
            auth.register_user(
                name="Alice Two",
                username="alicesmith",
                email="another@example.com",
                password="Password@123"
            )

        # Reject duplicate email
        with self.assertRaises(ValueError):
            auth.register_user(
                name="Alice Three",
                username="alice_new",
                email="alice@example.com",
                password="Password@123"
            )

        # Reject duplicate registration number
        with self.assertRaises(ValueError):
            auth.register_user(
                name="Alice Four",
                username="alice_four",
                email="alicefour@example.com",
                password="Password@123",
                registration_no="23BCON9999"
            )

    def test_complete_authentication_flow(self):
        """Test complete authentication flow:
        - Register student -> success confirmation
        - Login using username
        - Login using email
        - Login using registration number
        - Wrong password -> rejected
        - Duplicate registration number -> rejected
        - Account verification in database
        """
        # Step 1: Register student with registration number
        user_id = auth.register_user(
            name="Rohit Sharma",
            username="rohit_sharma",
            email="rohit@university.edu",
            password="SecurePassword@123",
            registration_no="23BCON7777"
        )
        self.assertGreater(user_id, 0)

        # Verification: Account exists in database
        db_user = database.get_user_by_id(user_id)
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user['username'], "rohit_sharma")
        self.assertEqual(db_user['registration_no'], "23BCON7777")

        # Step 2: Login using username
        auth_by_user = auth.authenticate("rohit_sharma", "SecurePassword@123")
        self.assertIsNotNone(auth_by_user)
        self.assertEqual(auth_by_user['id'], user_id)
        self.assertEqual(auth_by_user['username'], "rohit_sharma")

        # Step 3: Login using email
        auth_by_email = auth.authenticate("rohit@university.edu", "SecurePassword@123")
        self.assertIsNotNone(auth_by_email)
        self.assertEqual(auth_by_email['id'], user_id)

        # Step 4: Login using registration number (exact and case-insensitive)
        auth_by_reg = auth.authenticate("23BCON7777", "SecurePassword@123")
        self.assertIsNotNone(auth_by_reg)
        self.assertEqual(auth_by_reg['id'], user_id)

        auth_by_reg_lower = auth.authenticate("23bcon7777", "SecurePassword@123")
        self.assertIsNotNone(auth_by_reg_lower)
        self.assertEqual(auth_by_reg_lower['id'], user_id)

        # Step 5: Wrong password -> rejected
        self.assertIsNone(auth.authenticate("rohit_sharma", "WrongPassword!"))
        self.assertIsNone(auth.authenticate("rohit@university.edu", "WrongPassword!"))
        self.assertIsNone(auth.authenticate("23BCON7777", "WrongPassword!"))

        # Step 6: Duplicate registration number -> rejected
        with self.assertRaises(ValueError) as ctx:
            auth.register_user(
                name="Duplicate Rohit",
                username="rohit_duplicate",
                email="rohit_dup@university.edu",
                password="SecurePassword@123",
                registration_no="23BCON7777"
            )
        self.assertIn("already linked to another account", str(ctx.exception))

    def test_master_student_directory_import(self):
        """Verify master student directory was loaded with registration numbers and names."""
        amit = database.get_person_by_regno("23BCON0028")
        self.assertIsNotNone(amit)
        self.assertEqual(amit['name'], "AMIT AGARWAL")
        self.assertEqual(amit['type'], "student")
        self.assertEqual(amit['active'], 1)

        kanak = database.get_person_by_regno("23BCOL2259")
        self.assertIsNotNone(kanak)
        self.assertEqual(kanak['name'], "Kanak Tiwari")

        # Verify all 62 students from master list exist
        students = database.list_people(person_type="student", active_only=False)
        self.assertGreaterEqual(len(students), 62)

    def test_student_self_review_prevention_via_regno(self):
        """Do not allow a logged-in student to review themselves if account is linked to the same registration number."""
        amit_record = database.get_person_by_regno("23BCON0028")
        self.assertIsNotNone(amit_record)

        # Register user with the same registration number
        uid = auth.register_user(
            name="Amit Agarwal",
            username="amit_user",
            email="amit@student.univ.edu",
            password="Password@123",
            registration_no="23BCON0028"
        )

        # Attempt to review oneself should be rejected
        with self.assertRaises(ValueError) as ctx:
            database.submit_or_update_review(
                reviewer_id=uid,
                person_id=amit_record['id'],
                rating=5,
                review_text="Trying to give myself 5 stars"
            )
        self.assertIn("Self-review is not permitted", str(ctx.exception))

        # Also verify excluded from student list
        available = database.list_people(
            person_type="student",
            active_only=True,
            exclude_user_id=uid,
            exclude_regno="23BCON0028"
        )
        self.assertFalse(any(p['registration_no'] == "23BCON0028" for p in available))

    def test_admin_student_search_and_reviews_view(self):
        """Admin features: search by name, search by regno, view student reviews, view average rating, filter reviews by student."""
        # Create a reviewer
        reviewer_id = auth.register_user(
            name="Peer Reviewer",
            username="peer_rev",
            email="peer@univ.edu",
            password="Password@123"
        )

        amit = database.get_person_by_regno("23BCON0028")
        gaurav = database.get_person_by_regno("23BCON1758")

        # Submit review for Amit (5 stars)
        database.submit_or_update_review(
            reviewer_id=reviewer_id,
            person_id=amit['id'],
            rating=5,
            review_text="Excellent programming skills in Python and Web AI."
        )

        # Submit review for Gaurav (4 stars)
        database.submit_or_update_review(
            reviewer_id=reviewer_id,
            person_id=gaurav['id'],
            rating=4,
            review_text="Very good teamwork and active participation."
        )

        # 1. Search student by name
        name_results = database.get_students_summary(search_query="AMIT")
        self.assertTrue(any(s['registration_no'] == "23BCON0028" for s in name_results))

        # 2. Search by registration number
        reg_results = database.get_students_summary(search_query="23BCON1758")
        self.assertEqual(len(reg_results), 1)
        self.assertEqual(reg_results[0]['student_name'], "GAURAV VYAS")

        # 3. View average rating of each student
        amit_summary = [s for s in database.get_students_summary() if s['registration_no'] == "23BCON0028"][0]
        self.assertEqual(amit_summary['total_reviews'], 1)
        self.assertEqual(amit_summary['average_rating'], 5.0)

        # 4. View all reviews received by a student
        amit_reviews = database.get_student_reviews(amit['id'])
        self.assertEqual(len(amit_reviews), 1)
        self.assertEqual(amit_reviews[0]['reviewer_name'], "Peer Reviewer")
        self.assertIn("programming skills", amit_reviews[0]['review_text'])

        # 5. Filter reviews by student
        filtered_revs = database.fetch_admin_reviews(person_id=amit['id'])
        self.assertEqual(len(filtered_revs), 1)
        self.assertEqual(filtered_revs[0]['reviewed_person'], "AMIT AGARWAL")
        self.assertEqual(filtered_revs[0]['reviewed_person_regno'], "23BCON0028")

    def test_password_salts(self):
        pwd = "SecurePassword@123"
        h1 = auth.hash_password(pwd)
        h2 = auth.hash_password(pwd)
        self.assertNotEqual(h1, h2)
        self.assertTrue(auth.verify_password(pwd, h1))
        self.assertTrue(auth.verify_password(pwd, h2))
        self.assertFalse(auth.verify_password("OtherPassword", h1))

    def test_admin_seeding_and_secret_sync(self):
        os.environ.pop('ADMIN_PASSWORD', None)
        self.assertFalse(auth.seed_admin())
        self.assertFalse(auth.is_admin_configured())

        os.environ['ADMIN_PASSWORD'] = 'InitialPass@123'
        self.assertTrue(auth.seed_admin())
        self.assertTrue(auth.is_admin_configured())
        admin_user = auth.authenticate('admin', 'InitialPass@123')
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user['role'], 'admin')

        os.environ['ADMIN_PASSWORD'] = 'RotatedPass@456'
        self.assertTrue(auth.seed_admin())
        self.assertIsNone(auth.authenticate('admin', 'InitialPass@123'))
        new_admin = auth.authenticate('admin', 'RotatedPass@456')
        self.assertIsNotNone(new_admin)
        self.assertEqual(new_admin['username'], 'admin')

    def test_manage_people(self):
        teacher_id = database.add_person(
            name="Dr. Alan Turing",
            person_type="teacher",
            department="Computer Science"
        )
        self.assertGreater(teacher_id, 0)

        student_id = database.add_person(
            name="Grace Hopper",
            person_type="student",
            department="Software Engineering",
            registration_no="23BCON8888"
        )
        self.assertGreater(student_id, 0)

        teachers = database.list_people(person_type="teacher", active_only=False)
        self.assertTrue(any(t['name'] == "Dr. Alan Turing" for t in teachers))

        students = database.list_people(person_type="student", active_only=False)
        self.assertTrue(any(s['name'] == "Grace Hopper" for s in students))

        database.set_person_active(teacher_id, False)
        active_teachers = database.list_people(person_type="teacher", active_only=True)
        self.assertFalse(any(t['id'] == teacher_id for t in active_teachers))

        database.set_person_active(teacher_id, True)
        active_teachers = database.list_people(person_type="teacher", active_only=True)
        self.assertTrue(any(t['id'] == teacher_id for t in active_teachers))

    def test_duplicate_review_upsert(self):
        uid = auth.register_user(
            name="Bob Martin",
            username="bobmartin",
            email="bob@example.com",
            password="Password@123"
        )
        teacher_id = database.add_person("Dr. Evans", "teacher", "Physics")

        database.submit_or_update_review(
            reviewer_id=uid,
            person_id=teacher_id,
            rating=5,
            review_text="Initial review."
        )

        admin_revs = database.fetch_admin_reviews(person_id=teacher_id)
        self.assertEqual(len(admin_revs), 1)

        # Duplicate submission updates review
        database.submit_or_update_review(
            reviewer_id=uid,
            person_id=teacher_id,
            rating=4,
            review_text="Updated review text."
        )

        admin_revs_after = database.fetch_admin_reviews(person_id=teacher_id)
        self.assertEqual(len(admin_revs_after), 1)
        self.assertEqual(admin_revs_after[0]['rating'], 4)
        self.assertEqual(admin_revs_after[0]['review_text'], "Updated review text.")


if __name__ == '__main__':
    unittest.main()
