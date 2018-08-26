import datetime
import random

from factory.fuzzy import FuzzyFloat, FuzzyInteger

from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
from django.test import TestCase

from ..factories import TrashProfileFactory, HouseHoldFactory, TrashFactory
from ..models import TrackingPeriod
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

    def test_tracking_period_ends_accurate(self):
        """
        TrackingPeriod.began and TrackingPeriod.latest dates are accurate.
        """
        last_day = datetime.date.today() - datetime.timedelta(
            days=random.randint(1, 3))
        middle_day = last_day - datetime.timedelta(days=random.randint(1, 5))
        first_day = middle_day - datetime.timedelta(days=random.randint(1, 5))

        period = TrashFactory(date=last_day).tracking_period
        TrashFactory(date=middle_day, tracking_period=period)
        TrashFactory(date=first_day, tracking_period=period)
        period.refresh_from_db()

        self.assertEqual(period.began, first_day)
        self.assertEqual(period.latest, last_day)

    def test_create_trash_makes_tracking_period(self):
        """
        Creating a new trash prepares an empty tracking period if needed.
        """
        trash = TrashFactory()
        self.assertIsNot(trash.tracking_period, None)

    def test_create_trash_shares_tracking_period_as_appropriate(self):
        """
        Creating a new trash uses an existing tracking period as appropriate.
        """
        old_date = datetime.date.today() - datetime.timedelta(
            days=(settings.TRASHINATOR["MAX_TRACKING_SPLIT"] - 1))

        old_trash = TrashFactory(date=old_date)
        new_trash = TrashFactory(date=datetime.date.today(),
                                 household=old_trash.household)

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

    def test_tracking_periods_do_not_overlap_on_different_households(self):
        """
        Creating a new trash on a different household will not result in a
        shared tracking period.
        """
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        first_trash = TrashFactory(date=yesterday)

        user = first_trash.household.user
        user.current_household = HouseHoldFactory(user=user)
        user.save()

        second_trash = TrashFactory(household=user.current_household)

        self.assertNotEqual(first_trash.tracking_period.pk,
                            second_trash.tracking_period.pk)

    def test_tracking_period_class_closes_old_periods(self):
        """
        TrackingPeriod.close_old() will close records that are no
        longer accepting trash
        """
        cutoff = datetime.date.today() - datetime.timedelta(
            days=settings.TRASHINATOR["MAX_TRACKING_SPLIT"])
        past_cutoff = cutoff - datetime.timedelta(days=1)

        good = TrashFactory(date=datetime.date.today()).tracking_period
        TrashFactory(date=cutoff, tracking_period=good)

        must_close = TrashFactory(date=past_cutoff).tracking_period

        for i in range(random.randint(1, 3)):
            day = past_cutoff - datetime.timedelta(days=i)
            TrashFactory(date=day, tracking_period=must_close)

        void1 = TrashFactory(date=past_cutoff).tracking_period
        void2 = TrashFactory(date=past_cutoff).tracking_period

        closed, voided = TrackingPeriod.close_old()

        self.assertEqual(closed, 1, msg="should have closed 1")
        self.assertEqual(voided, 2, msg="should have voided 2")

        good.refresh_from_db()
        self.assertEqual(good.status, "PROGRESS")

        must_close.refresh_from_db()
        self.assertEqual(must_close.status, "COMPLETE")

        void1.refresh_from_db()
        self.assertEqual(void1.status, "VOID")

        void2.refresh_from_db()
        self.assertEqual(void2.status, "VOID")
