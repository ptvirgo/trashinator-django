import graphene
from graphene_django import DjangoObjectType
import statistics

from django.db.models import Count

from user_extensions import utils

from .models import Trash, TrackingPeriod, Stats, litres_to_gallons


# Trash Records

class TrashNode(DjangoObjectType):
    class Meta:
        model = Trash

    litres = graphene.Float(required=True)

    def resolve_litres(root, info):
        return root.litres

    gallons = graphene.Float(required=True)

    def resolve_gallons(root, info):
        return root.gallons


class TrashQuery(graphene.ObjectType):
    all_trash = graphene.List(TrashNode, token=graphene.String(required=True),
                              required=True)
    trash = graphene.Field(
        TrashNode,
        date=graphene.types.datetime.Date(required=True),
        token=graphene.String(required=True))

    def resolve_all_trash(self, info, token, **kwargs):
        """Collect all the User's Trash"""
        user = utils.jwt_user(token)

        if not user.is_authenticated:
            raise ValueError("not authorized")

        return Trash.objects.filter(household__user=user)

    def resolve_trash(self, info, date, token, **kwargs):
        user = utils.jwt_user(token)

        if not user.is_authenticated:
            raise ValueError("not authorized")

        try:
            return Trash.objects.get(household__user=user, date=date)
        except Trash.DoesNotExist:
            return


class Metric(graphene.Enum):
    Gallons = 1
    Litres = 2


class SaveTrash(graphene.Mutation):
    trash = graphene.Field(TrashNode, required=True)

    class Arguments:
        token = graphene.String(required=True)
        date = graphene.types.datetime.Date(required=True)
        metric = Metric()
        volume = graphene.Float()

    def mutate(self, info, token, date, metric=None, volume=None, **kwargs):
        user = utils.jwt_user(token)

        if not user.is_authenticated:
            raise ValueError("not authorized")

        try:
            trash = Trash.objects.get(household__user=user, date=date)
        except Trash.DoesNotExist:
            trash = Trash.create(
                household=user.trash_profile.current_household,
                date=date,
                litres=0)

        if volume is not None:
            if metric == Metric.Gallons:
                trash.gallons = volume
            elif metric == Metric.Litres:
                trash.litres = volume
            else:
                raise ValueError("metric must be litres or gallons")

            trash.save()

        return SaveTrash(trash=trash)


class TrashMutation(graphene.ObjectType):
    save_trash = SaveTrash.Field()


# Sitewide Stats

class SiteStatsNode(DjangoObjectType):
    class Meta:
        model = Stats

    litres_per_person_per_week = graphene.Float(required=True)
    litres_standard_deviation = graphene.Float(required=True)

    gallons_per_person_per_week = graphene.Float(required=True)
    gallons_standard_deviation = graphene.Float(required=True)

    def resolve_litres_per_person_per_week(root, info):
        return root.litres_per_person_per_week

    def resolve_standard_deviation_litres(root, info):
        return root.litres_standard_deviation

    def resolve_gallons_per_person_per_week(root, info):
        return root.gallons_per_person_per_week

    def resolve_standard_deviation_gallons(root, info):
        return root.gallons_standard_deviation


class UserStatsNode(graphene.ObjectType):
    """
    UserStatsNode is a "Node" without an underlying Django object.
    """

    litres_per_person_per_week = graphene.Float(required=True)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def _mean_per_week(self):
        """
        Get the mean litres per person per week for the user's tracking periods
        """
        periods = TrackingPeriod.objects.distinct().filter(
            trash__household__user=self.user).filter(
            status__in=["COMPLETE", "PROGRESS"]).annotate(
            trashes=Count("trash")).filter(trashes__gte=1)

        count = 0
        lpws = []

        for p in periods:
            lpw = p.litres_per_person_per_week

            if lpw is not None:
                count += 1
                lpws.append(lpw)

        if count > 0:
            mean = statistics.mean(lpws)
        else:
            mean = 0

        return mean

    def resolve_litres_per_person_per_week(self, info, *args, **kwargs):
        """
        Return the mean of litres per person per week for the user's tracking
        periods
        """
        if self.user is None:
            raise ValueError("user required")

        result = round(self._mean_per_week(), 2)
        return result

    gallons_per_person_per_week = graphene.Float(required=True)

    def resolve_gallons_per_person_per_week(self, info, *args, **kwargs):
        """
        Return the mean of gallons per person per week for the user's tracking
        periods
        """
        if self.user is None:
            raise ValueError("user required")

        result = round(litres_to_gallons(self._mean_per_week()), 2)
        return result


class StatsNode(graphene.ObjectType):
    user = None
    site = graphene.Field(SiteStatsNode, required=True)
    user = graphene.Field(UserStatsNode, required=True)

    def resolve_site(self, info, *args, **kwargs):
        stats = Stats.load()
        return stats

    def resolve_user(self, info, *ags, **kwargs):
        usn = UserStatsNode(user=self.user)
        return usn


class StatsQuery(graphene.ObjectType):

    stats = graphene.Field(
        StatsNode, required=True,
        token=graphene.String(required=True))

    def resolve_stats(self, info, token, *args, **kwargs):
        """Provide access to sitewide stats"""
        user = utils.jwt_user(token)

        if not user.is_authenticated:
            raise ValueError("not authorized")

        stats_node = StatsNode(user=user)
        return stats_node
