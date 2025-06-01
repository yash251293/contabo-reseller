from django.db import models
from django.contrib.auth.models import User

# Represents a hosting plan offered to customers.
# This model defines the specifications and pricing of a plan.
class HostingPlan(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the hosting plan (e.g., Basic, Pro).")
    disk_space_gb = models.IntegerField(help_text="Disk space in GB.")
    bandwidth_gb = models.IntegerField(help_text="Monthly bandwidth in GB.")
    email_accounts = models.IntegerField(help_text="Number of email accounts allowed.")
    databases = models.IntegerField(help_text="Number of databases allowed.")
    price_monthly = models.DecimalField(max_digits=6, decimal_places=2, help_text="Monthly price in USD.")

    # This field is crucial: it links this Django plan to a specific package name defined in CyberPanel.
    cyberpanel_package_name = models.CharField(
        max_length=100,
        help_text="The exact name of the corresponding package in CyberPanel."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this plan is currently available for new orders."
    )

    def __str__(self):
        return self.name

# Represents a specific hosting service instance provisioned for a customer.
# This links a customer to a hosting plan and their specific domain.
class CustomerService(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The customer who owns this service."
    )
    hosting_plan = models.ForeignKey(
        HostingPlan,
        on_delete=models.CASCADE,
        help_text="The hosting plan this service is based on."
    )
    domain_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The domain name associated with this service (e.g., mydomain.com)."
    )
    # Stores the username created on CyberPanel for this specific website/service.
    # This might be different from the Django panel's username.
    cyberpanel_username = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Username for this website on CyberPanel (for FTP, etc.)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this service was created in the panel."
    )
    # Reflects the status of the service in this panel (e.g., after admin actions).
    # Note: This might not always be in sync with the actual status in CyberPanel
    # without further integration (webhooks, periodic checks).
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the service is considered active in this panel."
    )

    def __str__(self):
        return f"{self.customer.username} - {self.domain_name}"
