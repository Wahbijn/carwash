# wash/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models.functions import TruncDate

from .models import Service, Booking, Vehicle
from .forms import BookingForm, VehicleForm

from django.views.generic import UpdateView

# ============================================================
#                    🔥 ADMIN DASHBOARD
# ============================================================
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):

    # -------------------------------
    #      GLOBAL STATISTICS
    # -------------------------------
    total_bookings = Booking.objects.exclude(status="cancelled").count()

    today_bookings = Booking.objects.filter(
        scheduled_date=timezone.now().date()
    ).exclude(status="cancelled").count()

    total_users = User.objects.count()

    total_revenue = Booking.objects.filter(
        status="done",
        service__price__isnull=False
    ).aggregate(total=Sum('service__price'))["total"] or 0


    # -------------------------------
    #           FILTERS
    # -------------------------------
    status_filter = request.GET.get("status")
    service_filter = request.GET.get("service")
    date_filter = request.GET.get("date")

    # -------------------------------
    #           SEARCH
    # -------------------------------
    search_query = request.GET.get("search", "")

    latest_bookings = Booking.objects.exclude(status="cancelled")

    if search_query:
        latest_bookings = latest_bookings.filter(
            Q(id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(service__name__istartswith=search_query) |   # FIX prefix-only match
            Q(vehicle__license_plate__icontains=search_query)
        )

    if status_filter:
        latest_bookings = latest_bookings.filter(status=status_filter)

    if service_filter:
        latest_bookings = latest_bookings.filter(service_id=service_filter)

    if date_filter:
        latest_bookings = latest_bookings.filter(scheduled_date=date_filter)

    latest_bookings = latest_bookings.order_by("-created_at")[:20]

    services = Service.objects.all()


    # -------------------------------
    #     CHART — BOOKINGS PER DAY
    # -------------------------------
    last_days = Booking.objects.exclude(status="cancelled") \
        .filter(created_at__date__gte=timezone.now().date() - timezone.timedelta(days=7)) \
        .annotate(day=TruncDate("created_at")) \
        .values("day") \
        .annotate(count=Count("id")) \
        .order_by("day")

    days = [str(item["day"]) for item in last_days]
    reservations_count = [item["count"] for item in last_days]


    # -------------------------------
    #     CHART — SERVICE STATS
    # -------------------------------
    service_stats = (
            Booking.objects
            .exclude(status="cancelled")
            .filter(service__isnull=False)
            .values("service__name")
            .annotate(count=Count("id"))
            .order_by("-count")
            )

    service_labels = [s["service__name"] for s in service_stats]
    service_counts = [s["count"] for s in service_stats]


    # -------------------------------
    #     🔥 NEW: CHART — TOP CLIENTS
    # -------------------------------
    top_clients = (
        Booking.objects
        .exclude(status="cancelled")
        .filter(user__isnull=False)
        .values("user__username")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    top_client_names = [c["user__username"] for c in top_clients]
    top_client_counts = [c["total"] for c in top_clients]


    # -------------------------------
    #     RETURN DATA TO TEMPLATE
    # -------------------------------
    return render(request, "wash/admin_dashboard.html", {
        "total_bookings": total_bookings,
        "today_bookings": today_bookings,
        "total_users": total_users,
        "total_revenue": total_revenue,

        "latest_bookings": latest_bookings,
        "days": days,
        "reservations_count": reservations_count,
        "service_labels": service_labels,
        "service_counts": service_counts,

        # filters + search
        "services": services,
        "status_filter": status_filter,
        "service_filter": service_filter,
        "date_filter": date_filter,
        "search_query": search_query,

        # NEW TOP CLIENTS DATA
        "top_client_names": top_client_names,
        "top_client_counts": top_client_counts,
    })



# ============================================================
#                   🔥 HOME PAGE (Auto-redirect admin)
# ============================================================
@login_required
def home(request):
    # Admin → dashboard admin
    if request.user.is_staff:
        return admin_dashboard(request)

    user = request.user

    # Bookings du user
    bookings = Booking.objects.filter(user=user)

    bookings_count = bookings.exclude(status="cancelled").count()

    vehicles_count = Vehicle.objects.filter(owner=user).count()

    total_spent = bookings.filter(
        status="done",
        service__price__isnull=False
    ).aggregate(total=Sum("service__price"))["total"] or 0

    next_booking = bookings.exclude(status="cancelled") \
        .filter(scheduled_date__gte=timezone.now().date()) \
        .order_by("scheduled_date") \
        .first()

    # 🔥 NOUVEAU : statistiques services (pour mini barres)
    service_usage = (
        Booking.objects
        .filter(user=user)
        .exclude(status="cancelled")
        .values("service__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    return render(request, "wash/home.html", {
        "bookings_count": bookings_count,
        "vehicles_count": vehicles_count,
        "total_spent": total_spent,
        "next_booking": next_booking,
        "service_usage": service_usage,   # ✅ envoyé au template
    })

# ============================================================
#                        SERVICES
# ============================================================
class ServiceListView(ListView):
    model = Service
    template_name = "wash/service_list.html"


class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    fields = ["name", "price", "duration_minutes"]
    template_name = "wash/service_form.html"
    success_url = reverse_lazy("services-list")


# ============================================================
#                        BOOKINGS
# ============================================================
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "wash/booking_form.html"
    success_url = reverse_lazy('bookings-list')
    login_url = '/accounts/login/'

    def get_initial(self):
        initial = super().get_initial()
        service_id = self.request.GET.get("service")
        if service_id:
            initial["service"] = service_id
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user

        if hasattr(obj, "created_at") and obj.created_at is None:
            obj.created_at = timezone.now()

        if obj.service and getattr(obj.service, "price", None) is not None:
            if hasattr(obj, "total_price"):
                obj.total_price = obj.service.price

        obj.save()
        if hasattr(form, "save_m2m"):
            form.save_m2m()

        messages.success(self.request, "Réservation créée.")
        return super().form_valid(form)


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "wash/booking_list.html"

    def get_queryset(self):
        qs = Booking.objects.filter(user=self.request.user).select_related('service', 'vehicle')
        if any(f.name == "status" for f in Booking._meta.fields):
            qs = qs.exclude(status='cancelled')

        if 'created_at' in [f.name for f in Booking._meta.fields]:
            return qs.order_by('-created_at')
        return qs.order_by('-pk')


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "wash/booking_detail.html"

    def get_queryset(self):
        return Booking.objects.select_related('service', 'vehicle', 'user') \
                              .filter(user=self.request.user)


class BookingCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)

        if booking.user_id != request.user.id:
            return HttpResponseForbidden("Not allowed")

        if any(f.name == "status" for f in Booking._meta.fields):
            booking.status = "cancelled"
            booking.save()
            messages.success(request, "Réservation annulée.")
        else:
            booking.delete()
            messages.success(request, "Réservation supprimée.")

        return redirect("bookings-list")


@login_required
@require_POST
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.status = 'cancelled'
    booking.save(update_fields=['status'])
    messages.success(request, "Réservation annulée.")
    return redirect('bookings-list')


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "wash/booking_form.html"
    success_url = reverse_lazy('bookings-list')

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


# ============================================================
#                        VEHICLES
# ============================================================
@login_required(login_url='/accounts/login/')
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.owner = request.user
            v.save()
            return redirect('bookings-create')
    else:
        form = VehicleForm()

    return render(request, 'wash/vehicle_form.html', {'form': form})


# ============================================================
#                    USER MANAGEMENT (ADMIN ONLY)
# ============================================================
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def users_list(request):
    search = request.GET.get("search", "")
    users = User.objects.filter(username__icontains=search).order_by("id")
    return render(request, "wash/users_list.html", {
        "users": users,
        "search": search
    })


@staff_member_required
def user_edit(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        if username:
            user.username = username
        if email:
            user.email = email

        user.save()
        messages.success(request, "Utilisateur mis à jour.")
        return redirect("users-list")

    return render(request, "wash/user_edit.html", {"user": user})


@staff_member_required
def user_delete(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    messages.success(request, "Utilisateur supprimé.")
    return redirect("users-list")





# ============================================================
#                    SERVICE MANAGEMENT
# ============================================================




class ServiceUpdateView(UpdateView):
    model = Service
    fields = ["name", "price", "duration_minutes"]
    template_name = "wash/service_form.html"
    success_url = reverse_lazy("services-list")

@login_required
def service_delete(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    service = get_object_or_404(Service, pk=pk)

    if request.method == "POST":
        service.delete()
        messages.success(request, "Service supprimé.")
        return redirect("services-list")

    return render(request, "wash/service_confirm_delete.html", {"service": service})
