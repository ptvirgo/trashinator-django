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

    def test_change_trash_household(self):
        """
        If the user changes their household and re-saves, the household on
        the re-save must be updated to match the current household
        """
        profile = TrashProfileFactory()
        trash = TrashFactory(household=profile.current_household)
        original_household = trash.household

        profile.current_household = HouseHoldFactory(user=profile.user)
        profile.save()

        test_data = {
            "date": trash.date.isoformat(),
            "metric": "Litres",
            "token": utils.user_jwt(profile.user)
        }

        query = """mutation
            SaveTrash($date: Date!, $token: String!, $metric: Metric!){
            saveTrash(date: $date, metric: $metric, token: $token){
            trash { date litres }}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        trash.refresh_from_db()
        self.assertEqual(trash.household.pk, profile.current_household.pk)
        self.assertNotEqual(trash.household.pk, original_household.pk)


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

    def test_tracking_period_stats_basic_math(self):
        """Do you even math bro?"""

        today = datetime.date.today()

        trash1 = TrashFactory(date=today)
        trash1.gallons = 5
        trash1.save()

        trash1.household.population = 4
        trash1.household.save()

        for i in range(3):
            date = today - datetime.timedelta(days=i+1)
            Trash.create(gallons=5, household=trash1.household, date=date,
                         tracking_period=trash1.tracking_period)

        self.assertEqual(
            trash1.tracking_period.gallons_per_person_per_week, 5,
            msg="model with single week: {}".format(
                trash1.household.trash_set.all()))

        six_months_ago = datetime.date.today() - datetime.timedelta(
            days=6 * 30)

        trash2 = TrashFactory(household=trash1.household, date=six_months_ago)
        trash2.gallons = 4
        trash2.save()

        for i in range(3):
            date = six_months_ago - datetime.timedelta(days=i+1)
            Trash.create(gallons=4, household=trash1.household, date=date,
                         tracking_period=trash2.tracking_period)

        self.assertEqual(
            trash2.tracking_period.gallons_per_person_per_week, 4,
            msg="model with two weeks: {}".format(
                trash1.household.trash_set.all()))

        user = trash1.household.user
        test_data = {"token": utils.user_jwt(user)}

        query = """query Stats($token: String!){stats(token: $token){
            user {gallonsPerPersonPerWeek gallonsPerPersonPerWeek}}}"""

        result = self.schema.execute(query, variable_values=test_data)

        if result.errors:
            raise AssertionError(result.errors)

        self.assertEqual(
            result.data["stats"]["user"]["gallonsPerPersonPerWeek"], 4.5)
