from django.test import TestCase

class YoutTestClass(TestCase):

    @classmethod
    def setUpClass(cls):
        # Importante poner super.setUpClass()
        super().setUpClass()
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        pass


    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")


    def test_false_is_false(self):
        print("Method: test_false_is_false")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true")
        self.assertTrue(True)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)