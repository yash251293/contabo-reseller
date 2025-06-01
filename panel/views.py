from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'panel/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'panel/login.html'

@login_required
def profile(request):
    return render(request, 'panel/profile.html')

from .models import HostingPlan, CustomerService
from .forms import OrderHostingForm
from .cyberpanel_api import CyberPanelAPI
from django.shortcuts import get_object_or_404
import secrets # For generating secure passwords

@login_required
def list_hosting_plans_view(request):
    plans = HostingPlan.objects.filter(is_active=True)
    return render(request, 'panel/list_hosting_plans.html', {'plans': plans})

@login_required
def order_hosting_plan_view(request, plan_id):
    plan = get_object_or_404(HostingPlan, id=plan_id, is_active=True)

    if request.method == 'POST':
        form = OrderHostingForm(request.POST)
        if form.is_valid():
            domain_name = form.cleaned_data['domain_name']

            # Generate a secure password for the CyberPanel account
            # This password will be for the website user on CyberPanel
            website_password = secrets.token_urlsafe(16)

            # For CyberPanel username, we can derive it from the domain or user's username
            # For simplicity, let's try to use a sanitized version of the panel username + part of domain
            # Ensure it meets CyberPanel's username requirements (e.g., length, characters)
            # A more robust strategy might be needed for production.
            base_cp_username = request.user.username.replace('.', '').replace('-', '')[:8]
            domain_prefix = domain_name.split('.')[0][:4]
            cyberpanel_username = f"{base_cp_username}{domain_prefix}"
            # Ensure username is unique or handle potential collisions if CyberPanel doesn't.

            api = CyberPanelAPI()
            api_response = api.create_website(
                domain_name=domain_name,
                package_name=plan.cyberpanel_package_name,
                owner_username=cyberpanel_username, # This is the username for the website on CyberPanel
                owner_password=website_password,
                owner_email=request.user.email,
                # php_version can be a setting or part of the plan
            )

            # Simulate successful API response for now as per subtask instructions
            # In a real scenario, check api_response for success status and details
            # e.g. if 'websiteStatus' in api_response and api_response['websiteStatus'] == 'success':
            simulated_success = True # Replace with actual API response check

            if simulated_success: # Check based on actual API response structure
                # Assuming API call was successful
                customer_service = CustomerService.objects.create(
                    customer=request.user,
                    hosting_plan=plan,
                    domain_name=domain_name,
                    cyberpanel_username=cyberpanel_username # Store the username used/returned by CP
                    # is_active can be True by default
                )
                # Optionally, store the generated password securely if needed for the user,
                # or instruct them it's been set and they should change it via CyberPanel if possible.
                # For this example, we are not storing the website_password in our database.
                return redirect('order_success') # Or a page showing service details
            else:
                # Handle API error
                error_message = api_response.get("error", "An unknown error occurred with the hosting provider.")
                if 'createWebsiteStatus' in api_response and api_response['createWebsiteStatus'] == 0: # Example error check
                     error_message = api_response.get('error_message', error_message)
                form.add_error(None, f"Could not create website: {error_message}")

    else:
        form = OrderHostingForm()

    return render(request, 'panel/order_hosting_plan.html', {'form': form, 'plan': plan})

@login_required
def order_success_view(request):
    # A simple success page
    return render(request, 'panel/order_success.html')

@login_required
def customer_services_view(request):
    services = CustomerService.objects.filter(customer=request.user)
    # Nameservers and FTP host will be added to context, likely from settings
    # For FTP host, we can try to derive from CYBERPANEL_API_URL or use a dedicated setting
    from django.conf import settings

    # Attempt to parse hostname from CYBERPANEL_API_URL
    # This is a simplistic parsing, assumes URL like https://hostname:port/api
    try:
        api_url_parts = settings.CYBERPANEL_API_URL.split('/')
        # Expected: ['https:', '', 'hostname:port', 'api', ''] or similar
        ftp_hostname = api_url_parts[2].split(':')[0] if len(api_url_parts) > 2 else settings.CYBERPANEL_HOSTNAME
    except AttributeError: # CYBERPANEL_HOSTNAME might not be set yet
        ftp_hostname = "your_server_ip_or_hostname" # Fallback
    except IndexError: # CYBERPANEL_API_URL might be malformed for this parsing
        ftp_hostname = settings.CYBERPANEL_HOSTNAME # Fallback to dedicated setting


    context = {
        'services': services,
        'primary_nameserver': getattr(settings, 'PRIMARY_NAMESERVER', 'ns1.example.com'),
        'secondary_nameserver': getattr(settings, 'SECONDARY_NAMESERVER', 'ns2.example.com'),
        'ftp_hostname': getattr(settings, 'CYBERPANEL_HOSTNAME', ftp_hostname)
    }
    return render(request, 'panel/customer_services.html', context)
