from django.db import models

class HostingPlan(models.Model):
    name = models.CharField(max_length=100)
    disk_space_gb = models.IntegerField()
    bandwidth_gb = models.IntegerField()
    email_accounts = models.IntegerField()
    databases = models.IntegerField()
    price_monthly = models.DecimalField(max_digits=6, decimal_places=2)
    cyberpanel_package_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

from django.contrib.auth.models import User

class CustomerService(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    hosting_plan = models.ForeignKey(HostingPlan, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=255, unique=True)
    cyberpanel_username = models.CharField(max_length=100, blank=True, null=True) # Stores username from CyberPanel
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer.username} - {self.domain_name}"
