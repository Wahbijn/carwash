# wash/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from psycopg2 import DatabaseError
from .models import Service, Booking, Vehicle
from .forms import BookingForm, VehicleForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


# --- Services ---
class ServiceListView(ListView):
    model = Service
    template_name = "wash/service_list.html"


class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    fields = ["name", "description", "price", "duration_minutes"]
    template_name = "wash/service_form.html"
    success_url = reverse_lazy("services-list")


# --- Bookings ---
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "wash/booking_form.html"
    success_url = reverse_lazy('bookings-list')
    login_url = '/accounts/login/'

    def get_form_kwargs(self):
        """Passe request.user au formulaire pour limiter la queryset des véhicules."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Save avec commit=False pour assigner user avant insertion en DB,
        puis save() et save_m2m() si besoin.
        """
        # crée l'instance sans l'enregistrer encore en DB
        obj = form.save(commit=False)

        # obligatoire : assigner l'utilisateur connecté
        obj.user = self.request.user

        # si tu as un champ created_at auto rempli manuellement:
        if hasattr(obj, "created_at") and obj.created_at is None:
            obj.created_at = timezone.now()

        # calcul serveur si tu veux (prix total etc.)
        try:
            if obj.service and getattr(obj.service, "price", None) is not None:
                # si tu as un champ total_price dans Booking
                if hasattr(obj, "total_price"):
                    obj.total_price = obj.service.price
        except Exception:
            pass

        # maintenant on peut sauver
        obj.save()

        # m2m (si applicables)
        if hasattr(form, "save_m2m"):
            form.save_m2m()

        # message d'info facultatif
        messages.success(self.request, "Réservation créée.")

        # super().form_valid(form) s'attend à self.object = obj et fait la redirection
        self.object = obj
        return super().form_valid(form)
    
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "wash/booking_list.html"

    def get_queryset(self):
        # uniquement réservations de l'utilisateur connecté, avec service+vehicle chargés
        qs = Booking.objects.filter(user=self.request.user).select_related('service', 'vehicle')

        # par défaut on masque les réservations annulées
        if any(f.name == "status" for f in Booking._meta.fields):
            qs = qs.exclude(status='cancelled')

        # tri : préfère created_at si présent
        field_names = {f.name for f in Booking._meta.fields}
        if 'created_at' in field_names:
            return qs.order_by('-created_at')

        order_fields = []
        if 'scheduled_date' in field_names:
            order_fields.append('-scheduled_date')
        if 'scheduled_time' in field_names:
            order_fields.append('-scheduled_time')
        order_fields.append('-pk')
        return qs.order_by(*order_fields)


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "wash/booking_detail.html"

    def get_queryset(self):
        # restreint aux réservations de l'utilisateur (sécurité)
        return Booking.objects.select_related('service', 'vehicle', 'user').filter(user=self.request.user)

class BookingCancelView(LoginRequiredMixin, View):
    """
    Annule une réservation (POST uniquement). On marque 'status' = 'cancelled'
    si le modèle a un champ status, sinon on supprime la réservation.
    """
    def post(self, request, pk, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=pk)
        # sécurité : l'utilisateur ne peut annuler que sa réservation
        if booking.user_id != request.user.id:
            return HttpResponseForbidden("Not allowed")

        if any(f.name == "status" for f in Booking._meta.fields):
            booking.status = "cancelled"
            booking.save(update_fields=["status"])
            messages.success(request, "Réservation annulée.")
        else:
            booking.delete()
            messages.success(request, "Réservation supprimée.")

        return redirect("bookings-list")
# Fonction simple pour annuler une réservation (POST uniquement)
@login_required
@require_POST
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    # marque comme annulée (ou utilises booking.delete() si tu veux supprimer)
    if any(f.name == "status" for f in Booking._meta.fields):
        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        messages.success(request, "Réservation annulée.")
    else:
        # si pas de champ status, supprime (option sûre)
        booking.delete()
        messages.success(request, "Réservation supprimée.")
    return redirect('bookings-list')

class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "wash/booking_form.html"  # peut être le même que la création
    success_url = reverse_lazy('bookings-list')
    login_url = '/accounts/login/'

    def get_queryset(self):
        # l'utilisateur ne peut éditer que ses propres réservations
        return Booking.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # passe l'utilisateur au formulaire (important pour limiter vehicle queryset)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # tu peux garder la même logique que pour la création si besoin
        obj = form.save(commit=False)
        # ensure owner remains the same (defensive)
        obj.user = self.request.user
        obj.save()
        if hasattr(form, "save_m2m"):
            form.save_m2m()
        return super().form_valid(form)

# --- Vehicles ---
@login_required(login_url='/accounts/login/')
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.owner = request.user
            v.save()
            return redirect('vehicles-list')
    else:
        form = VehicleForm()
    return render(request, 'wash/vehicle_form.html', {'form': form})


def home(request):
    return render(request, 'wash/home.html')
