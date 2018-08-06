import datetime

import graphene
from graphene_django import DjangoObjectType

from user_extensions import utils

from .models import Trash


class TrashNode(DjangoObjectType):
    class Meta:
        model = Trash

    litres = graphene.Float()

    def resolve_litres(root, info):
        return root.litres

    gallons = graphene.Float()

    def resolve_gallons(root, info):
        return root.gallons


class TrashQuery(graphene.ObjectType):
    all_trash = graphene.List(TrashNode, token=graphene.String(required=True))
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

        return Trash.objects.get(household__user=user, date=date)


class Metric(graphene.Enum):
    Gallons = 1
    Litres = 2


class SaveTrash(graphene.Mutation):
    trash = graphene.Field(TrashNode)

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
            trash = Trash(
                household=user.trash_profile.current_household,
                date=datetime.date.today(),
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
