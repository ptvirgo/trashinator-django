import datetime
from enum import Enum
from math import ceil
import pycountry
import statistics

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from .validators import zero_or_more, one_or_more


# Helpers

def litres_to_gallons(litres):
    return litres / 3.785411784


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

    def __str__(self):
        return "TrashProfile(user={}, created={})".format(
            self.user.username, self.created.isoformat())


class HouseHold(models.Model):
    """
    HouseHold describes minimal population and location data for Trash records,
    and connects them back to the original TrashProfile
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    population = models.IntegerField(validators=[one_or_more])
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES)

    def __str__(self):
        return


class TrackingPeriodStatus(Enum):
    """
    Tracking period status choices.
    """
    PROGRESS = "in progress"
    COMPLETE = "complete"
    VOID = "void"


class TrackingPeriod(models.Model):
    """
    TrackingPeriod represents a time period during which a user provided
    regular updates.
    """
    status = models.CharField(
        max_length=8,
        choices=([(s.name, s.value) for s in TrackingPeriodStatus]),
        default=TrackingPeriodStatus.PROGRESS.name,
        null=False)

    @property
    def began(self):
        item = self.trash_set.order_by("date").first()

        if item is not None:
            return item.date
        else:
            return None

    @property
    def latest(self):
        item = self.trash_set.order_by("-date").first()

        if item is not None:
            return item.date
        else:
            return None

    @property
    def _volume_per_person_per_week(self):
        if self.status == "VOID":
            return

        if not self.trash_set.exists:
            return

        volume = self.trash_set.aggregate(models.Sum("_volume"))
        litres = volume["_volume__sum"]

        pop = self.trash_set.first().household.population

        day_count = self.latest - self.began
        weeks = ceil(day_count.days / 7.0)

        if weeks == 0:
            weeks = 1

        return litres / pop / weeks

    @property
    def litres_per_person_per_week(self):
        """
        Provide the volume in litres / person / week, rounded to two decimals
        """
        volume = self._volume_per_person_per_week

        if volume == 0:
            return

        return round(self._volume_per_person_per_week, 2)

    @property
    def gallons_per_person_per_week(self):
        """
        Provide the volume in gallons / person / week, rounded to two decimals
        """
        volume = self._volume_per_person_per_week

        if volume == 0:
            return

        return round(litres_to_gallons(self._volume_per_person_per_week), 2)

    @classmethod
    def close_old(cls):
        """
        Change TrackingPeriod.status to COMPLETE or VOID for TrackingPeriods
        whose last record is older than the settings allow.  TrackingPeriods
        require at least two Trash records to be marked COMPLETE.

        Returns:
            two integers: number of COMPLETE records and number of VOID records
        """
        cutoff = datetime.date.today() - datetime.timedelta(
            days=settings.TRASHINATOR["MAX_TRACKING_SPLIT"])

        completes = TrackingPeriod.objects.annotate(
            latest=models.Max("trash__date"),
            total=models.Count("trash")
            ).filter(status="PROGRESS", latest__lt=cutoff, total__gt=1)

        completes_count = completes.count()
        completes.update(status="COMPLETE")

        voids = TrackingPeriod.objects.annotate(
            latest=models.Max("trash__date"),
            total=models.Count("trash")
            ).filter(status="PROGRESS", latest__lt=cutoff, total__lt=2)

        void_count = voids.count()
        voids.update(status="VOID")

        return completes_count, void_count


class Trash(models.Model):
    """
    Trash records keep track of actual volume.  Stored in litres.
    """
    class Meta:
        unique_together = (("date", "household"))

    _volume = models.FloatField(validators=[zero_or_more])

    date = models.DateField()
    household = models.ForeignKey("HouseHold", on_delete=models.PROTECT)
    tracking_period = models.ForeignKey(
        "TrackingPeriod", on_delete=models.CASCADE)

    def clean(self):
        user = self.household.user
        conflicts = Trash.objects.filter(household__user=user).\
            exclude(household=self.household).filter(date=self.date)

        if conflicts.exists():
            raise ValidationError(
                "can't have multiple trash records for same user on same day")

    @classmethod
    def create(cls, household, *args, **kwargs):
        last_trash = Trash.objects.filter(
            household=household).order_by("-date").first()

        cutoff = datetime.date.today() - datetime.timedelta(
            days=settings.TRASHINATOR["MAX_TRACKING_SPLIT"])

        if "tracking_period" in kwargs:
            tracking_period = kwargs.pop("tracking_period")
        elif last_trash is not None \
                and (last_trash.tracking_period.status ==
                     TrackingPeriodStatus.PROGRESS.name) \
                and (last_trash.tracking_period.latest > cutoff):
            tracking_period = last_trash.tracking_period
        else:
            tracking_period = TrackingPeriod.objects.create()

        trash = cls(*args, household=household,
                    tracking_period=tracking_period, **kwargs)
        return trash

    @property
    def litres(self):
        return round(self._volume, 2)

    @litres.setter
    def litres(self, litres):
        self._volume = litres

    @property
    def gallons(self):
        return round(litres_to_gallons(self._volume), 2)

    @gallons.setter
    def gallons(self, gallons):
        self._volume = gallons * 3.785411784

    def __str__(self):
        return "Trash(user={}, date={}, _volume={})".format(
            self.household.user.username, self.date.isoformat(), self._volume)


class Stats(models.Model):
    """
    Stats provides the means to periodically calculate and store app
    statistics, so that the calculations don't have to be re-made on every
    look-up.
    """
    _volume_per_person_per_week = models.FloatField(default=0)
    _volume_standard_deviation = models.FloatField(default=0)

    @property
    def litres_per_person_per_week(self):
        return round(self._volume_per_person_per_week, 2)

    @property
    def gallons_per_person_per_week(self):
        return round(litres_to_gallons(self._volume_per_person_per_week), 2)

    @property
    def litres_standard_deviation(self):
        return round(self._volume_standard_deviation, 2)

    @property
    def gallons_standard_deviation(self):
        return round(litres_to_gallons(self._volume_standard_deviation), 2)

    def recalculate(self):
        periods = TrackingPeriod.objects.filter(
            status__in=["PROGRESS", "COMPLETE"]).annotate(
            trashes=models.Count("trash")).filter(trashes__gte=1)

        count = periods.count()

        lpws = [p.litres_per_person_per_week for p in periods]

        if count > 0:
            self._volume_per_person_per_week = statistics.mean(lpws)

        if count > 1:
            self._volume_standard_deviation = statistics.stdev(lpws)

        self.save()

    @classmethod
    def create(cls, *args, **kwargs):
        obj, created = cls.objects.get_or_create(pk=1)
        obj.recalculate()
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
