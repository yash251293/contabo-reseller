from django.contrib import admin, messages
from .models import HostingPlan, CustomerService

class HostingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_monthly', 'disk_space_gb', 'bandwidth_gb', 'is_active', 'cyberpanel_package_name')
    list_filter = ('is_active',)
    search_fields = ('name', 'cyberpanel_package_name')

admin.site.register(HostingPlan, HostingPlanAdmin)

class CustomerServiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'domain_name', 'hosting_plan', 'cyberpanel_username', 'created_at', 'is_active')
    list_filter = ('is_active', 'hosting_plan', 'created_at')
    search_fields = ('domain_name', 'customer__username', 'cyberpanel_username')
    readonly_fields = ('created_at',)

    # Admin actions
    def suspend_selected_services(modeladmin, request, queryset):
        from .cyberpanel_api import CyberPanelAPI
        api = CyberPanelAPI()
        success_count = 0
        error_count = 0
        for service in queryset:
            # Simulate API call success as per subtask instructions
            # response = api.suspend_website(domain_name=service.domain_name)
            # if response.get('status') == 'success' or response.get('SomeSuccessIndicatorField'): # Adjust based on actual API
            simulated_api_success = True # Replace with actual API call and check
            if simulated_api_success:
                service.is_active = False
                service.save()
                success_count += 1
            else:
                error_count += 1
                # modeladmin.message_user(request, f"Failed to suspend {service.domain_name}: {response.get('error_message', 'Unknown error')}", messages.ERROR)
        if success_count:
            modeladmin.message_user(request, f"Successfully suspended {success_count} service(s).")
        if error_count:
            modeladmin.message_user(request, f"Failed to suspend {error_count} service(s).", messages.ERROR) # Requires messages import
    suspend_selected_services.short_description = "Suspend selected CyberPanel accounts"

    def unsuspend_selected_services(modeladmin, request, queryset):
        from .cyberpanel_api import CyberPanelAPI
        api = CyberPanelAPI()
        success_count = 0
        error_count = 0
        for service in queryset:
            simulated_api_success = True # Replace with actual API call and check
            if simulated_api_success:
                service.is_active = True
                service.save()
                success_count += 1
            else:
                error_count += 1
        if success_count:
            modeladmin.message_user(request, f"Successfully unsuspended {success_count} service(s).")
        if error_count:
            modeladmin.message_user(request, f"Failed to unsuspend {error_count} service(s).", messages.ERROR)
    unsuspend_selected_services.short_description = "Unsuspend selected CyberPanel accounts"

    def delete_selected_services(modeladmin, request, queryset):
        from .cyberpanel_api import CyberPanelAPI
        api = CyberPanelAPI()
        success_count = 0
        error_count = 0
        for service in queryset:
            simulated_api_success = True # Replace with actual API call and check
            if simulated_api_success:
                # Optionally, instead of deleting the CustomerService object, mark it inactive
                # and perhaps add a 'deleted_in_cyberpanel' flag.
                # For this example, we'll mark as inactive.
                service.is_active = False
                # service.delete() # If you want to remove it from the panel database
                service.save()
                success_count += 1
            else:
                error_count += 1
        if success_count:
            modeladmin.message_user(request, f"Successfully initiated deletion for {success_count} service(s) in CyberPanel and marked as inactive.")
        if error_count:
            modeladmin.message_user(request, f"Failed to delete {error_count} service(s) in CyberPanel.", messages.ERROR)
    delete_selected_services.short_description = "Delete selected CyberPanel accounts (marks inactive)"

    actions = [suspend_selected_services, unsuspend_selected_services, delete_selected_services]

admin.site.register(CustomerService, CustomerServiceAdmin)
