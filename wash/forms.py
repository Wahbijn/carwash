from django import forms
from .models import Booking, Service, Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make','model','license_plate']


class ServiceModelChoiceField(forms.ModelChoiceField):
    """Affiche le nom du service + prix dans les radios."""
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.price} TND)"


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["vehicle", "service", "scheduled_date", "scheduled_time"]
        widgets = {
            "service": forms.RadioSelect(),
            "scheduled_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "scheduled_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "vehicle": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # 1️⃣ SERVICES — supprimer l’option vide
        self.fields["service"].queryset = Service.objects.all().order_by("name")
        self.fields["service"].required = True
        self.fields["service"].empty_label = None  # 👈 enlève les "--------"

        # 2️⃣ VEHICLES — afficher seulement ceux du user + texte personnalisé
        if user is not None and user.is_authenticated:
            qs = Vehicle.objects.filter(owner=user).order_by("license_plate")
            self.fields["vehicle"].queryset = qs
            self.fields["vehicle"].empty_label = "Choisir un véhicule"  # 👈 ton label personnalisé
        else:
            self.fields["vehicle"].queryset = Vehicle.objects.none()

        self.fields["vehicle"].required = True


    def clean_vehicle(self):
        vehicle = self.cleaned_data.get("vehicle")
        if vehicle and self.user and vehicle.owner != self.user:
            raise forms.ValidationError("Ce véhicule n'appartient pas à l'utilisateur connecté.")
        return vehicle


class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["scheduled_date", "scheduled_time"]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type":"date", "class":"form-control"}),
            "scheduled_time": forms.TimeInput(attrs={"type":"time", "class":"form-control"}),
        }
