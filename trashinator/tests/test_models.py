from datetime import date
from factory.fuzzy import FuzzyFloat, FuzzyInteger

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..factories import TrashProfileFactory, HouseHoldFactory, TrashFactory


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
                                          date=date(2018, 1, 1))
        same_user_diff_day.validate_unique()

        # Same user same day should be invalid
        same_user_same_day = TrashFactory(household=profile.current_household)
        self.assertRaises(ValidationError, same_user_same_day.validate_unique)

        # Same same day with different household is still invalid
        new_house = HouseHoldFactory(user=profile.user)
        why = TrashFactory(household=new_house)
        self.assertRaises(ValidationError, why.clean)

    def test_trash_volume_validation(self):
        """Trash volume cannot be below 0"""
        low = FuzzyFloat(-10, -0.1)
        trash = TrashFactory(volume=low)
        self.assertRaises(ValidationError, trash.clean_fields)

    def test_household_population_validation(self):
        """Household size cannot be below 1"""
        low = FuzzyInteger(-10, 0)
        household = HouseHoldFactory(population=low)
        self.assertRaises(ValidationError, household.clean_fields)
