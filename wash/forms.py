from django import forms
from .models import Booking, Service, Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'license_plate']


class ServiceModelChoiceField(forms.ModelChoiceField):
    """Affiche le nom du service + prix dans les radios."""
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.price} TND)"


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ["vehicle", "service", "scheduled_date", "scheduled_time"]
        widgets = {
            "scheduled_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "scheduled_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "vehicle": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.no_vehicle = False  # flag pour le template

        # --------------------------
        #  SERVICE FIELD (radio)
        # --------------------------
        self.fields["service"] = ServiceModelChoiceField(
            queryset=Service.objects.all().order_by("name"),
            widget=forms.RadioSelect(),
            empty_label=None
        )

        # --------------------------
        #  VEHICLE FIELD
        # --------------------------
        if user and user.is_authenticated:
            qs = Vehicle.objects.filter(owner=user).order_by("license_plate")
            self.fields["vehicle"].queryset = qs
            self.fields["vehicle"].empty_label = "Choisir un véhicule"

            # aucun véhicule → désactiver + signaler au template
            if qs.count() == 0:
                self.fields["vehicle"].widget.attrs["disabled"] = True
                self.no_vehicle = True
        else:
            self.fields["vehicle"].queryset = Vehicle.objects.none()

        self.fields["vehicle"].required = True

    # sécurité : éviter qu’un user choisisse le véhicule d’un autre
    def clean_vehicle(self):
        vehicle = self.cleaned_data.get("vehicle")
        if self.user and vehicle and vehicle.owner != self.user:
            raise forms.ValidationError("Ce véhicule ne vous appartient pas.")
        return vehicle


class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["scheduled_date", "scheduled_time"]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type":"date", "class":"form-control"}),
            "scheduled_time": forms.TimeInput(attrs={"type":"time", "class":"form-control"}),
        }
