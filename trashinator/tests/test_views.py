import datetime
import random

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Trash
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


class TestSubmitTrash(TestCase):

    def test_post_trash(self):
        """Trash can be created via POST"""
        profile = TrashProfileFactory(system="U")
        client = Client()
        client.force_login(profile.user)

        today = datetime.date.today().isoformat()
        test_data = {today: random.randint(1, 13)}

        response = client.post(reverse("trashinator:trash"), test_data)
        self.assertEqual(response.status, 200)
        record = Trash.objects.filter(household=profile.current_household).\
            filter(date=today)

        self.assertEqual(record.gallons, test_data[today])

    def test_post_metric(self):
        """Trash posts with metric system are converted"""
        profile = TrashProfileFactory(system="M")
        client = Client()
        client.force_login(profile.user)

        today = datetime.date.today().isoformat()
        test_data = {today: random.randint(1, 13)}

        response = client.post(reverse("trashinator:trash"), test_data)
        self.assertEqual(response.status, 200)
        record = Trash.objects.filter(household=profile.current_household).\
            filter(date=today)

        self.assertEqual(record.litres, test_data[today])

    def test_backdate_trash_forms(self):
        """
        Trash forms are back-dated up to three days when records are missing.
        """
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(1)
        two_days_ago = yesterday - datetime.timedelta(1)
        five_days_ago = today - datetime.timedelta(5)
        one_week_ago = today - datetime.timedelta(7)
        
        profile = TrashProfileFactory(created=one_week_ago)

        client = Client()
        client.force_login(profile.user)

        response = client.get(reverse("trashinator:trash"))
        self.assertEqual(response.status, 200)

        # When no records are present, an older profile will produce a request
        # for no more than three records
        self.assertContains(response, today.isoformat())
        self.assertContains(response, yesterday.isoformat())
        self.assertContains(response, two_days_ago.isoformat())
        self.assertDoesNotContain(response, five_days_ago.isoformat())
        self.assertDoesNotContain(response, one_week_ago.isoformat())

        TrashFactory(household=profile.current_household, date=today)
        TrashFactory(household=profile.current_household, date=yesterday)

        response = client.get(reverse("trashinator:trash"))
        self.assertEqual(response.status, 200)
        self.assertDoesNotContain(response, yesterday.isoformat(),
            msg="failed to remove request for available record")
        self.assertContains(response, today.isoformat(),
            msg="today's record should always be editable")
        self.assertContains(response, two_days_ago.isoformat(),
            msg="missing record from two days ago should be requested")
