from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.chainvet.models import Assessment, Order
from apps.users.models import CustomUser, Affiliate

# Register your models here.
class AffiliateUserEmailFilter(admin.SimpleListFilter):
    # Human-readable title for the filter
    title = _('affiliate user email')

    # Parameter for the filter that will be used in the URL query
    parameter_name = 'affiliate_user_email'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value
        for the option that will appear in the URL query. The second element is the
        human-readable name for the option that will appear in the right sidebar.
        """
        # You might want to adjust this query to return a more manageable list
        # of email addresses or implement a more dynamic approach.
        emails = CustomUser.objects.filter(affiliate__isnull=False).values_list('email', flat=True).distinct()
        return [(email, email) for email in emails]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string
        and retrievable via `self.value()`.
        """
        if self.value():
            return queryset.filter(access_code__affiliate_origin__user__email=self.value())
        return queryset
class AssessmentAdmin(admin.ModelAdmin):
    list_filter = [AffiliateUserEmailFilter, 'user', 'access_code', 'type_of_assessment', 'is_mock' ]
admin.site.register(Assessment, AssessmentAdmin)


class CreatedAfterLaunchFilter(admin.SimpleListFilter):
    title = 'Since launch'  # The title displayed on the admin
    parameter_name = 'created_after_launch'  # URL parameter

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value 
        for the option that will appear in the URL query. The second element is the 
        human-readable name for the option that will appear in the right sidebar.
        """
        return (
            ('created_after_launch', 'After Launch'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string.
        """
        if self.value() == 'created_after_launch':
            cutoff_date = django_tz.datetime(2024, 2, 29)
            return queryset.filter(created_at__gt=cutoff_date)
        return queryset
class OrderAdmin(admin.ModelAdmin):
    list_filter=['created_at', 'status', 'is_paid', CreatedAfterLaunchFilter]
admin.site.register(Order, OrderAdmin)
# admin.site.register(PreOrder)