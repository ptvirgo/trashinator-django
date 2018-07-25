from django import forms

from .models import COUNTRY_CHOICES, SYSTEM_CHOICES
from .validators import zero_or_more, one_or_more


class TrashProfileForm(forms.Form):
    system = forms.ChoiceField(
        choices=SYSTEM_CHOICES, label="Measurement system", initial="I")
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES, label="Country", initial="USA")
    population = forms.IntegerField(
        label="Household size", validators=[one_or_more], initial=1)


class TrashForm(forms.Form):
    def __init__(self, system, dates, *args, **kwargs):
        """
        Prepare a Trash form.

        Args:
        system: "imperial" or "metric," determines whether label will read
        "gallons" or "liters"

        dates: list of datetime.dates for which the user should provide
        estimates
        """

        super().__init__(*args, **kwargs)

        if len(dates) < 1 or len(dates) > 3:
            raise ValueError(
                "TrashForm supports 1 - 3 dates, got " + len(dates))

        if system == "imperial":
            unit = "gallon"
        else:
            unit = "litre"

        for d in dates:
            date = d.isoformat()
            label = "On %s, how many %ss of trash did you take out?" %\
                    (date, unit)
            self.fields[date] = forms.FloatField(
                label=label, required=True, validators=[zero_or_more])
