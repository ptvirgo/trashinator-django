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
    trash = graphene.Field(TrashNode, date=graphene.String(required=True),
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


class SaveTrash(graphene.Mutation):
    hello = graphene.String()

    class Arguments:
        name = graphene.String(required=True)

    def mutate(self, info, name, **kwargs):
        return SaveTrash(hello=name)


class TrashMutation(graphene.ObjectType):
    mutate_trash = SaveTrash.Field()
