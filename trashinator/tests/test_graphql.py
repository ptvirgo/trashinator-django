import datetime
import graphene
import random

from django.test import TestCase

from user_extensions import utils

from ..factories import TrashProfileFactory, HouseHoldFactory, TrashFactory,\
    TrackingPeriodFactory
from ..models import Trash, Stats
from ..schema import TrashQuery, TrashMutation, StatsQuery


class TestReadTrash(TestCase):
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
        test_data = {"token": utils.user_jwt(profile.user)}

        query = """query AllTrash($token: String!){
            allTrash(token: $token){date litres gallons}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(len(result.data["allTrash"]),
                         len(current_trash) + len(old_trash))

    def test_read_trash(self):
        """User can retrieve a single trash record"""
        profile = TrashProfileFactory()
        trash = TrashFactory(household=profile.current_household)

        # make sure we don't pick up other people's trash
        TrashFactory(date=trash.date)

        test_data = {"token": utils.user_jwt(profile.user),
                     "date": trash.date.isoformat()}

        query = """query TrashQuery($token: String!, $date: Date!){
                   trash(token: $token, date: $date){date gallons}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(result.data["trash"]["date"], trash.date.isoformat())
        self.assertEqual(result.data["trash"]["gallons"], trash.gallons)


class TestSaveTrash(TestCase):
    schema = graphene.Schema(query=TrashQuery, mutation=TrashMutation)

    def test_save_trash(self):
        """Trash can be saved"""
        profile = TrashProfileFactory()

        test_data = {
            "date": datetime.date.today().isoformat(),
            "metric": "Gallons",
            "volume": float(random.randint(1, 10)),
            "token": utils.user_jwt(profile.user)
        }

        query = """mutation
            SaveTrash($date: Date!, $token: String!, $metric: Metric!,
                      $volume: Float){
            saveTrash(date: $date, metric: $metric, volume: $volume,
                      token: $token){
            trash { date gallons }}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(
            result.data["saveTrash"]["trash"]["gallons"], test_data["volume"])

        lookup = Trash.objects.get(
            household=profile.current_household, date=test_data["date"])

        self.assertEqual(lookup.gallons, test_data["volume"])

    def test_resave_trash(self):
        """Trash can be overwritten"""

        profile = TrashProfileFactory()
        TrashFactory(household=profile.current_household)

        test_data = {
            "date": datetime.date.today().isoformat(),
            "metric": "Litres",
            "volume": float(random.randint(1, 10)),
            "token": utils.user_jwt(profile.user)
        }

        query = """mutation
            SaveTrash($date: Date!, $token: String!, $metric: Metric!,
                      $volume: Float){
            saveTrash(date: $date, metric: $metric, volume: $volume,
                      token: $token){
            trash { date litres }}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(
            result.data["saveTrash"]["trash"]["litres"], test_data["volume"])

        lookup = Trash.objects.get(
            household=profile.current_household, date=test_data["date"])

        self.assertEqual(lookup.litres, test_data["volume"])


class TestReadStats(TestCase):
    schema = graphene.Schema(query=StatsQuery)

    def test_read_site_stats(self):
        """Sitewide stats can be read"""
        trash = TrashFactory()
        user = trash.household.user
        TrackingPeriodFactory.from_trash(trash, 5)
        stats = Stats.create()
        stats.save()
        test_data = {"token": utils.user_jwt(user)}

        query = """query Stats($token: String!){stats(token: $token){
            site {litresPerPersonPerWeek gallonsPerPersonPerWeek
                  litresStandardDeviation gallonsStandardDeviation}}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(
            result.data["stats"]["site"]["litresPerPersonPerWeek"],
            stats.litres_per_person_per_week)

        self.assertEqual(
            result.data["stats"]["site"]["gallonsPerPersonPerWeek"],
            stats.gallons_per_person_per_week)

        self.assertEqual(
            result.data["stats"]["site"]["litresStandardDeviation"],
            stats.litres_standard_deviation)

        self.assertEqual(
            result.data["stats"]["site"]["gallonsStandardDeviation"],
            stats.gallons_standard_deviation)

    def test_read_user_stats(self):
        """User stats can be read"""
        trash = TrashFactory()
        user = trash.household.user
        period = TrackingPeriodFactory.from_trash(trash, 5)

        test_data = {"token": utils.user_jwt(user)}

        query = """query Stats($token: String!){stats(token: $token){
            user {litresPerPersonPerWeek gallonsPerPersonPerWeek}}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(
            result.data["stats"]["user"]["litresPerPersonPerWeek"],
            period.litres_per_person_per_week)

        self.assertEqual(
            result.data["stats"]["user"]["gallonsPerPersonPerWeek"],
            period.gallons_per_person_per_week)
