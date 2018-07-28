import graphene
import random

from django.test import TestCase

from user_extensions import utils

from ..factories import TrashProfileFactory, HouseHoldFactory, TrashFactory
from ..schema import TrashQuery, TrashMutation


class TestGraphql(TestCase):
    schema = graphene.Schema(query=TrashQuery, mutation=TrashMutation)

    def test_read_all_trash(self):
        """User can retrieve all trash records"""

        profile = TrashProfileFactory()
        old_house = HouseHoldFactory(user=profile.user)

        current_trash = [TrashFactory(household=profile.current_household)
                         for _ in range(random.randint(1, 3))]

        old_trash = [TrashFactory(household=old_house)
                     for _ in range(random.randint(1, 3))]

        TrashFactory()  # don't pick up other people's trash

        query = """{allTrash(token: "%s"){date litres gallons}}""" %\
            (utils.user_jwt(profile.user),)
        result = self.schema.execute(query)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(len(result.data["allTrash"]),
                         len(current_trash) + len(old_trash))

    def test_read_trash(self):
        """User can retrieve a single trash record"""
        profile = TrashProfileFactory()
        trash = TrashFactory(household=profile.current_household)
        TrashFactory(date=trash.date)  # don't pick up other people's trash

        query = """{trash(token: "%s", date: "%s"){date gallons}}""" %\
            (utils.user_jwt(profile.user), trash.date.isoformat())

        result = self.schema.execute(query)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(result.data["trash"]["date"], trash.date.isoformat())
        self.assertEqual(result.data["trash"]["gallons"], trash.gallons)
