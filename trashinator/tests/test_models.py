import datetime

from factory.fuzzy import FuzzyFloat, FuzzyInteger
from unittest import skip

from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
from django.test import TestCase

from ..factories import TrashProfileFactory, HouseHoldFactory, TrashFactory
# from ..models import TrashManage, TrackingPeriod, TrackingPeriodStatus


class TestTrash(TestCase):
    """
    Test Trashinator Models
    """

    def test_trash_daily_limit(self):
        """One trash record per person, per day"""

        profile = TrashProfileFactory()
        first = TrashFactory(household=profile.current_household)
        first.validate_unique()

        # New user same day should be fine
        profile2 = TrashProfileFactory()
        new_user_same_day = TrashFactory(household=profile2.current_household)
        new_user_same_day.validate_unique()

        # Same user different day should be fine
        same_user_diff_day = TrashFactory(household=profile.current_household,
                                          date=datetime.date(2018, 1, 1))
        same_user_diff_day.validate_unique()

        # Same same day with different household is invalid
        new_house = HouseHoldFactory(user=profile.user)
        why = TrashFactory(household=new_house, date=first.date)
        self.assertRaises(ValidationError, why.clean)

        # Same user same day should be invalid
        self.assertRaises(
            IntegrityError, TrashFactory,
            **{"household": profile.current_household, "date": first.date})

    def test_trash_volume_validation(self):
        """Trash volume cannot be below 0"""
        low = FuzzyFloat(-10, -0.1)
        trash = TrashFactory(gallons=low)
        self.assertRaises(ValidationError, trash.clean_fields)

    def test_trash_volume_conversions(self):
        """Trash volume can be read in gallons or litres"""
        trash = TrashFactory()
        trash.litres = 5
        self.assertEqual(trash.litres, 5.0)
        trash.gallons = 2.5
        self.assertEqual(trash.gallons, 2.5)
        self.assertEqual(trash.litres / 3.785411784, trash.gallons)

    def test_household_population_validation(self):
        """Household size cannot be below 1"""
        low = FuzzyInteger(-10, 0)
        household = HouseHoldFactory(population=low)
        self.assertRaises(ValidationError, household.clean_fields)

    def test_trash_profile_current_houshold_owner(self):
        """
        TrashProfile user and TrashProfile.household.user must be
        identical
        """
        # current_household with the same user is fine
        profile1 = TrashProfileFactory()
        new_household = HouseHoldFactory(user=profile1.user)
        profile1.current_household = new_household
        profile1.clean()

        # current_household with a different user raises ValidationError
        profile2 = TrashProfileFactory()
        profile1.current_household = profile2.current_household
        self.assertRaises(ValidationError, profile1.clean)


class TestTrackingPeriod(TestCase):

    def test_create_trash_makes_tracking_period(self):
        """
        Creating a new trash prepares an empty tracking period if needed.
        """
        trash = TrashFactory()
        self.assertEqual(len(trash.tracking_period_set), 1)

    def test_create_trash_shares_tracking_period_as_appropriate(self):
        """
        Creating a new trash uses an existing tracking period as appropriate.
        """
        old_date = datetime.date.today() - datetime.timedelta(
            days=settings.TRASHINATOR["MAX_TRACKING_SPLIT"])

        old_trash = TrashFactory(date=old_date)
        new_trash = TrashFactory(household=old_trash.household)

        self.assertEqual(old_trash.tracking_period.pk,
                         new_trash.tracking_period.pk)

    def test_create_trash_splits_tracking_period_as_appropriate(self):
        """
        Creating a new trash splits tracking periods as appropriate.
        """
        old_date = datetime.date.today() - datetime.timedelta(
            days=(settings.TRASHINATOR["MAX_TRACKING_SPLIT"] + 1))

        old_trash = TrashFactory(date=old_date)
        new_trash = TrashFactory(household=old_trash.household)

        self.assertNotEqual(old_trash.tracking_period.pk,
                            new_trash.tracking_period.pk)

    @skip("TODO")
    def test_tracking_period_is_open(self):
        """
        TrackingPeriod is closed after the
        settings.trashinator.max_quiet_period has passed
        """
        raise AssertionError("not written")
