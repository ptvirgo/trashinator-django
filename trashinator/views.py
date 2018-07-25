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

            if hasattr(request.user, "trash_profile"):
                profile = request.user.trash_profile
            else:
                profile = TrashProfile(user=request.user)

            try:
                household = HouseHold.objects.get(
                    user=request.user,
                    population=form.cleaned_data["population"],
                    country=form.cleaned_data["country"])
            except HouseHold.DoesNotExist:
                household = HouseHold(
                    user=request.user,
                    population=form.cleaned_data["population"],
                    country=form.cleaned_data["country"])

            household.save()

            profile.system = form.cleaned_data["system"]
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
