import datetime
import pycountry

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from .validators import zero_or_more, one_or_more

# Model choices


SYSTEM_CHOICES = (("U", "US"), ("M", "Metric"))
COUNTRY_CHOICES = tuple((c.alpha_3, c.name) for c in pycountry.countries)

# Models


class TrashProfile(models.Model):
    """
    User Profile details specific to the Trashinator
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="trash_profile")

    current_household = models.OneToOneField(
        "HouseHold", on_delete=models.PROTECT, related_name="active_profile")
    system = models.CharField(max_length=1, choices=SYSTEM_CHOICES)

    created = models.DateField(default=datetime.date.today)

    def clean(self):
        if self.current_household.user.pk != self.user.pk:
            raise ValidationError(
                "current_household cannot belong to someone else")

class HouseHold(models.Model):
    """
    HouseHold describes minimal population and location data for Trash records,
    and connects them back to the original TrashProfile
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    population = models.IntegerField(validators=[one_or_more])
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES)


class Trash(models.Model):
    """
    Trash records keep track of actual volume.  Stored in litres.
    """
    class Meta:
        unique_together = (("date", "household"))
    date = models.DateField()
    household = models.ForeignKey("HouseHold", on_delete=models.PROTECT)
    _volume = models.FloatField(validators=[zero_or_more])

    def clean(self):
        user = self.household.user
        conflicts = Trash.objects.filter(household__user=user).\
            exclude(household=self.household).filter(date=self.date)

        if conflicts.exists():
            raise ValidationError(
                "can't have multiple trash records for same user on same day")
    @property
    def litres(self):
        return self._volume

    @litres.setter
    def litres(self, litres):
        self._volume = litres

    @property
    def gallons(self):
        return self._volume / 3.785411784

    @gallons.setter
    def gallons(self, gallons):
        self._volume = gallons * 3.785411784
