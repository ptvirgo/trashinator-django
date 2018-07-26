from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import TrashProfile, HouseHold, Trash
from .forms import TrashProfileForm, TrashForm


class TrashProfileView(LoginRequiredMixin, View):
    """Create a user profile"""

    form_class = TrashProfileForm
    template_name = "trashinator/trash_profile_form.html"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            if hasattr(request.user, "trash_profile"):
                profile = request.user.trash_profile
            else:
                profile = TrashProfile(user=request.user)

            household = self.updated_household(
                request.user, data["population"], data["country"])

            profile.system = data["system"]
            profile.current_household = household
            profile.save()
            status = 200

        else:
            status = 400

        return render(
            request, self.template_name, {"form": form}, status=status)

    def get(self, request, *args, **kwargs):

        if hasattr(request.user, "trash_profile"):
            profile = request.user.trash_profile
            form_data = {"system": profile.system,
                         "country": profile.current_household.country,
                         "population": profile.current_household.population}
        else:
            form_data = None

        form = self.form_class(form_data)
        return render(request, self.template_name, {"form": form})

    @staticmethod
    def updated_household(user, population, country):
        """Get or create the household as described"""
        try:
            household = HouseHold.objects.get(
                user=user, population=population, country=country)
        except HouseHold.DoesNotExist:
            household = HouseHold(
                user=user, population=population, country=country)
            household.save()

        return household
