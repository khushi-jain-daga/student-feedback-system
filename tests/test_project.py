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

    def test_structured_student_evaluation_and_resubmission(self):
        """Verify multi-criteria structured evaluation for students with score breakdown and overall rating."""
        reviewer_id = auth.register_user(
            name="Student Evaluator",
            username="evaluator1",
            email="evaluator1@univ.edu",
            password="Password@123"
        )
        amit = database.get_person_by_regno("23BCON0028")
        self.assertIsNotNone(amit)

        criteria = database.get_evaluation_criteria("student")
        self.assertEqual(len(criteria), 9)

        # 9 scores: e.g. five 5s and four 4s -> sum = 41 / 9 = 4.56 -> rounded to 5 star rating
        test_scores = [
            {'key': c['key'], 'label': c['label'], 'category': c['category'], 'score': 5 if i % 2 == 0 else 4}
            for i, c in enumerate(criteria)
        ]

        rev_id = database.submit_or_update_review(
            reviewer_id=reviewer_id,
            person_id=amit['id'],
            review_text="Strong problem solving and excellent teamwork in labs.",
            scores=test_scores
        )
        self.assertGreater(rev_id, 0)

        # Verify review record
        rev = database.fetch_one('SELECT * FROM reviews WHERE id = ?', (rev_id,))
        self.assertIsNotNone(rev)
        self.assertEqual(rev['rating'], 5)
        self.assertAlmostEqual(rev['overall_rating'], 4.56, places=2)

        # Verify review_scores rows
        saved_scores = database.get_review_scores(rev_id)
        self.assertEqual(len(saved_scores), 9)

        # Category scores
        cat_scores = database.get_review_category_scores(rev_id)
        self.assertIn("Academics", cat_scores)
        self.assertIn("Behaviour & Conduct", cat_scores)

        # Resubmission (Update) with changed scores: all 3s
        updated_scores = [
            {'key': c['key'], 'label': c['label'], 'category': c['category'], 'score': 3}
            for c in criteria
        ]
        rev_id_2 = database.submit_or_update_review(
            reviewer_id=reviewer_id,
            person_id=amit['id'],
            review_text="Needs to engage more in class discussions.",
            scores=updated_scores
        )
        self.assertEqual(rev_id, rev_id_2)

        # No duplicates created
        all_revs = database.fetch_admin_reviews(person_id=amit['id'])
        self.assertEqual(len(all_revs), 1)

        rev_updated = database.fetch_one('SELECT * FROM reviews WHERE id = ?', (rev_id,))
        self.assertEqual(rev_updated['rating'], 3)
        self.assertEqual(rev_updated['overall_rating'], 3.0)

        # Exactly 9 scores remain (previous scores replaced)
        new_scores = database.get_review_scores(rev_id)
        self.assertEqual(len(new_scores), 9)
        self.assertTrue(all(s['score'] == 3 for s in new_scores))

    def test_structured_teacher_evaluation_and_analytics(self):
        """Verify structured evaluation for teachers and institutional evaluation analytics."""
        reviewer_id = auth.register_user(
            name="Faculty Evaluator",
            username="evaluator2",
            email="evaluator2@univ.edu",
            password="Password@123"
        )
        teacher_id = database.add_person("Prof. Ada Lovelace", "teacher", "Computer Science")

        teacher_crit = database.get_evaluation_criteria("teacher")
        self.assertEqual(len(teacher_crit), 9)

        scores = [
            {'key': c['key'], 'label': c['label'], 'category': c['category'], 'score': 5}
            for c in teacher_crit
        ]

        rev_id = database.submit_or_update_review(
            reviewer_id=reviewer_id,
            person_id=teacher_id,
            review_text="Masterful pedagogy and outstanding student guidance.",
            scores=scores
        )
        self.assertGreater(rev_id, 0)

        # Test evaluation analytics
        analytics = database.get_evaluation_analytics()
        self.assertIn('teacher_category_averages', analytics)
        self.assertIn('top_criteria', analytics)
        self.assertIn('user_participation', analytics)

        # Export helper
        export_data = database.fetch_all_structured_scores_for_export()
        self.assertGreaterEqual(len(export_data), 9)
        self.assertTrue(any(row['reviewed_person'] == "Prof. Ada Lovelace" for row in export_data))

    def test_password_reset_workflow(self):
        """Verify admin-assisted password reset request creation and resolution."""
        req_id = database.create_password_reset_request("lost_user@univ.edu", "Forgotten student credentials")
        self.assertGreater(req_id, 0)

        resets = database.get_password_reset_requests()
        matching = [r for r in resets if r['id'] == req_id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]['status'], 'pending')
        self.assertEqual(matching[0]['identifier'], "lost_user@univ.edu")

        # Resolve request
        ok = database.resolve_password_reset_request(req_id)
        self.assertTrue(ok)

        resets_after = database.get_password_reset_requests()
        resolved = [r for r in resets_after if r['id'] == req_id][0]
        self.assertEqual(resolved['status'], 'resolved')

    def test_registration_student_master_verification(self):
        """When require_master_match=True, verify that registration requires valid student record."""
        # Unmatched registration number
        with self.assertRaises(ValueError) as ctx:
            auth.register_user(
                name="Fake Student",
                username="fakestudent",
                email="fake@univ.edu",
                password="Password@123",
                registration_no="99NONEXISTENT",
                require_master_match=True
            )
        self.assertIn("not found in the verified student directory", str(ctx.exception))

        # Matched registration number succeeds
        uid = auth.register_user(
            name="Amit Agarwal",
            username="amit_matched",
            email="amit_matched@univ.edu",
            password="Password@123",
            registration_no="23BCON0028",
            require_master_match=True
        )
        self.assertGreater(uid, 0)

    def test_privacy_rules_and_data_isolation(self):
        """Verify strict privacy rules:
        - Normal users cannot see other reviewers' comments or identities.
        - User query methods only return user's own submissions.
        - Received reviews cannot be accessed by normal user accounts.
        """
        # User 1 submits a review for student Amit
        user1_id = auth.register_user(
            name="Confidential Reviewer",
            username="confidential1",
            email="confidential1@univ.edu",
            password="Password@123"
        )
        amit = database.get_person_by_regno("23BCON0028")

        database.submit_or_update_review(
            reviewer_id=user1_id,
            person_id=amit['id'],
            rating=5,
            review_text="Confidential constructive evaluation."
        )

        # User 2 logs in
        user2_id = auth.register_user(
            name="Independent User",
            username="user2",
            email="user2@univ.edu",
            password="Password@123"
        )

        # User 2 has not submitted a review for Amit
        u2_rev = database.get_user_review_for_person(user2_id, amit['id'])
        self.assertIsNone(u2_rev)

        # User 2 reviewed list does not contain Amit
        u2_reviewed = database.get_user_reviewed_person_ids(user2_id)
        self.assertNotIn(amit['id'], u2_reviewed)

        # User 1 reviewed list contains Amit
        u1_reviewed = database.get_user_reviewed_person_ids(user1_id)
        self.assertIn(amit['id'], u1_reviewed)

        # Amit as a registered user cannot see reviews submitted about him
        amit_user_id = auth.register_user(
            name="Amit Agarwal",
            username="amit_account",
            email="amit_acc@univ.edu",
            password="Password@123",
            registration_no="23BCON0028"
        )
        amit_own_reviews = database.get_user_reviewed_person_ids(amit_user_id)
        self.assertEqual(len(amit_own_reviews), 0)


if __name__ == '__main__':
    unittest.main()

