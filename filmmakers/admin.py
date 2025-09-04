# filmmakers/admin.py
from django.contrib import admin, messages
from django.db.models import Sum
from .models import FilmmakerApplication
from payments.models import Payout, Order

@admin.register(FilmmakerApplication)
class FilmmakerApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'bio')
    actions = ['approve_applications', 'reject_applications', 'process_payouts']

    def approve_applications(self, request, queryset):
        for application in queryset.filter(status=FilmmakerApplication.Status.PENDING):
            application.approve()
    approve_applications.short_description = "Approve selected applications and upgrade user role"

    def reject_applications(self, request, queryset):
        for application in queryset.filter(status=FilmmakerApplication.Status.PENDING):
            application.reject()
    reject_applications.short_description = "Reject selected applications"

    def process_payouts(self, request, queryset):
        for application in queryset.filter(status=FilmmakerApplication.Status.APPROVED):
            filmmaker = application.user
            if not filmmaker.mpesa_payout_number:
                self.message_user(request, f"Error: Filmmaker {filmmaker.email} has no M-Pesa number set.", level=messages.ERROR)
                continue

            unpaid_orders = Order.objects.filter(film__filmmaker=filmmaker, status=Order.SUCCESS, payout__isnull=True)
            total_payout = unpaid_orders.aggregate(total=Sum('filmmaker_payout'))['total'] or 0

            if total_payout > 0:
                new_payout = Payout.objects.create(filmmaker=filmmaker, amount=total_payout)
                # mpesa_b2c_payout(filmmaker.mpesa_payout_number, total_payout) # This would be called in a real scenario
                unpaid_orders.update(payout=new_payout)
                self.message_user(request, f"Payout of KES {total_payout} initiated for {filmmaker.email}.", level=messages.SUCCESS)
            else:
                self.message_user(request, f"No unpaid earnings for {filmmaker.email}.", level=messages.INFO)
    process_payouts.short_description = "Process M-Pesa payouts for selected filmmakers"