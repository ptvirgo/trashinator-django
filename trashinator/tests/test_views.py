from django.test import Client, TestCase
from django.urls import reverse

from ..factories import TrashProfileFactory


class TestSubmitProfile(TestCase):

    def test_post_settings(self):
        """Profile and HouseHold settings can be updated via form post"""
        profile = TrashProfileFactory()
        client = Client()
        client.force_login(profile.user)

        japan = {"system": "M", "country": "JPN", "population": 3}
        usa = {"system": "U", "country": "USA", "population": 1}

        response = client.post(reverse("trashinator:profile"), japan)
        profile.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile.system, japan["system"])
        self.assertEqual(profile.current_household.country, japan["country"])
        self.assertEqual(profile.current_household.population,
                         japan["population"])

        response = client.post(reverse("trashinator:profile"), usa)
        profile.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile.system, usa["system"])
        self.assertEqual(profile.current_household.country, usa["country"])
        self.assertEqual(profile.current_household.population,
                         usa["population"])
