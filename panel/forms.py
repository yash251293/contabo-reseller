from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

from django import forms
from .models import HostingPlan

class OrderHostingForm(forms.Form):
    domain_name = forms.CharField(
        max_length=255,
        label="Domain Name",
        help_text="Enter the domain you want to host, e.g., yourdomain.com"
    )
    # Hosting plan will be passed from the view/URL, not selected by user in this form directly

    def clean_domain_name(self):
        domain_name = self.cleaned_data.get('domain_name')
        # Basic validation: ensure it's not just whitespace and looks somewhat like a domain.
        # More sophisticated validation (e.g., regex for domain structure, checking DNS) can be added.
        if not domain_name or len(domain_name.strip()) == 0:
            raise forms.ValidationError("Domain name cannot be empty.")
        if len(domain_name.split('.')) < 2:
            raise forms.ValidationError("Please enter a valid domain name (e.g., yourdomain.com).")
        # You might also want to check if a CustomerService with this domain already exists,
        # though the model's unique=True on domain_name will also catch this at the DB level.
        return domain_name
