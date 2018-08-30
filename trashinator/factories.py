from datetime import date, timedelta
import factory
import factory.fuzzy

from user_extensions.factories import UserFactory

from . import models

TEST_SYSTEM_CHOICES = [s[0] for s in models.SYSTEM_CHOICES]
TEST_COUNTRY_CHOICES = [c[0] for c in models.COUNTRY_CHOICES]


class TrashProfileFactory(factory.django.DjangoModelFactory):
    """Dummy TrashProfile"""
    class Meta:
        model = models.TrashProfile

    user = factory.SubFactory(UserFactory)
    system = factory.fuzzy.FuzzyChoice(TEST_SYSTEM_CHOICES)

    current_household = factory.SubFactory(
        "trashinator.factories.HouseHoldFactory",
        user=factory.SelfAttribute("..user"))


class HouseHoldFactory(factory.django.DjangoModelFactory):
    """Dummy HouseHold"""
    class Meta:
        model = models.HouseHold

    user = factory.SubFactory(UserFactory)
    population = factory.fuzzy.FuzzyInteger(1, 8)
    country = factory.fuzzy.FuzzyChoice(TEST_COUNTRY_CHOICES)


class TrashFactory(factory.django.DjangoModelFactory):
    """Dummy Trash"""
    class Meta:
        model = models.Trash

    @factory.sequence
    def date(x):
        return date.today() - timedelta(x)

    household = factory.SubFactory("trashinator.factories.HouseHoldFactory")
    gallons = factory.fuzzy.FuzzyFloat(0, 13)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        trash = model_class.create(*args, **kwargs)
        trash.save()
        return trash


class TrackingPeriodFactory(factory.django.DjangoModelFactory):
    """TrackingPeriod"""
    class Meta:
        model = models.TrackingPeriod

    status = "PROGRESS"

    @staticmethod
    def from_trash(first, count, *args, **kwargs):

        for i in range(count):
            day = first.date - timedelta(days=(i + 1))
            TrashFactory(date=day, household=first.household,
                         tracking_period=first.tracking_period)

        first.tracking_period.save()
        return first.tracking_period
