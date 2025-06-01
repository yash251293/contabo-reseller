from django.contrib import admin, messages
from .models import HostingPlan, CustomerService

# Configuration for HostingPlan model in Django admin.
class HostingPlanAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view.
    list_display = ('name', 'price_monthly', 'disk_space_gb', 'bandwidth_gb', 'is_active', 'cyberpanel_package_name')
    # Filters available in the admin sidebar.
    list_filter = ('is_active',)
    # Fields searchable in the admin list view.
    search_fields = ('name', 'cyberpanel_package_name')

admin.site.register(HostingPlan, HostingPlanAdmin)

# Configuration for CustomerService model in Django admin.
class CustomerServiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'domain_name', 'hosting_plan', 'cyberpanel_username', 'created_at', 'is_active')
    list_filter = ('is_active', 'hosting_plan', 'created_at')
    search_fields = ('domain_name', 'customer__username', 'cyberpanel_username')
    readonly_fields = ('created_at',) # Make created_at read-only in the edit form.

    # Admin actions
    # Action to suspend selected customer services.
    def suspend_selected_services(modeladmin, request, queryset):
        # modeladmin: The ModelAdmin instance.
        # request: The current HttpRequest.
        # queryset: A QuerySet containing the set of selected CustomerService objects.
        from .cyberpanel_api import CyberPanelAPI
        api = CyberPanelAPI()
        success_count = 0
        error_count = 0
        for service in queryset: # Iterate over selected CustomerService objects.
            # IMPORTANT: This is a simulation. In a real system, make the actual API call:
            # response = api.suspend_website(domain_name=service.domain_name)
            # Check response for success, e.g., if response.get('status') == 'success' or specific CyberPanel success indicators.
            simulated_api_success = True # TODO: Replace with actual API call and success check.

            if simulated_api_success:
                service.is_active = False # Mark the service as inactive in the panel.
                service.save()
                success_count += 1
            else:
                error_count += 1
                # Display an error message for this specific service.
                # Example: modeladmin.message_user(request, f"Failed to suspend {service.domain_name}: {response.get('error_message', 'Unknown API error')}", messages.ERROR)

        # Display summary messages to the admin.
        if success_count:
            modeladmin.message_user(request, f"Successfully suspended {success_count} service(s).")
        if error_count:
            # Note: messages.ERROR is used for error level messages.
            modeladmin.message_user(request, f"Failed to suspend {error_count} service(s). Please check logs if individual errors were not displayed.", messages.ERROR)
    suspend_selected_services.short_description = "Suspend selected CyberPanel accounts" # Text displayed in the admin actions dropdown.

    # Action to unsuspend selected customer services.
    def unsuspend_selected_services(modeladmin, request, queryset):
        from .cyberpanel_api import CyberPanelAPI
        api = CyberPanelAPI()
        success_count = 0
        error_count = 0
        for service in queryset:
            # SIMULATED API CALL - Replace with actual API interaction and response checking.
            simulated_api_success = True # TODO: Replace with actual API call and success check.
            if simulated_api_success:
                service.is_active = True # Mark the service as active in the panel.
                service.save()
                success_count += 1
            else:
                error_count += 1
                # Example: modeladmin.message_user(request, f"Failed to unsuspend {service.domain_name}: {response.get('error_message', 'Unknown API error')}", messages.ERROR)
        if success_count:
            modeladmin.message_user(request, f"Successfully unsuspended {success_count} service(s).")
        if error_count:
            modeladmin.message_user(request, f"Failed to unsuspend {error_count} service(s).", messages.ERROR)
    unsuspend_selected_services.short_description = "Unsuspend selected CyberPanel accounts"

    # Action to delete selected customer services from CyberPanel.
    def delete_selected_services(modeladmin, request, queryset):
        from .cyberpanel_api import CyberPanelAPI
        api = CyberPanelAPI()
        success_count = 0
        error_count = 0
        for service in queryset:
            # SIMULATED API CALL - Replace with actual API interaction and response checking.
            simulated_api_success = True # TODO: Replace with actual API call and success check.
            if simulated_api_success:
                # Instead of deleting the CustomerService object from the panel's database,
                # we mark it as inactive. This preserves the record for history
                # but indicates it's no longer active/managed in CyberPanel via this action.
                # A 'deleted_in_cyberpanel_at' DateTimeField could also be added for more precise tracking.
                service.is_active = False
                # To actually delete from panel DB: service.delete()
                service.save()
                success_count += 1
            else:
                error_count += 1
                # Example: modeladmin.message_user(request, f"Failed to delete {service.domain_name} from CyberPanel: {response.get('error_message', 'Unknown API error')}", messages.ERROR)
        if success_count:
            modeladmin.message_user(request, f"Successfully initiated deletion for {success_count} service(s) in CyberPanel and marked as inactive in this panel.")
        if error_count:
            modeladmin.message_user(request, f"Failed to delete {error_count} service(s) in CyberPanel.", messages.ERROR)
    delete_selected_services.short_description = "Delete selected CyberPanel accounts (marks inactive in panel)"

    # Register the actions with the admin class, making them available in the dropdown.
    actions = [suspend_selected_services, unsuspend_selected_services, delete_selected_services]

admin.site.register(CustomerService, CustomerServiceAdmin) # Register CustomerService model with its custom admin configuration.
