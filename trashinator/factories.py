from datetime import date
import factory
import factory.fuzzy

from django.contrib.auth import get_user_model

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

    date = date.today()
    household = factory.SubFactory("trashinator.factories.HouseHoldFactory")
    gallons = factory.fuzzy.FuzzyFloat(0, 13)
