from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm
from django.urls import reverse # Added for panel_index_view

# View for user registration.
def register(request):
    # Handles POST request: if form is valid, save user, log them in, and redirect to profile.
    # Handles GET request: displays an empty registration form.
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

# Displays the user's profile page.
# Requires user to be logged in.
@login_required
def profile(request):
    return render(request, 'panel/profile.html')

from .models import HostingPlan, CustomerService
from .forms import OrderHostingForm
from .cyberpanel_api import CyberPanelAPI
from django.shortcuts import get_object_or_404
import secrets # For generating secure passwords for CyberPanel accounts

# Displays a list of active hosting plans available for ordering.
# Requires user to be logged in.
@login_required
def list_hosting_plans_view(request):
    plans = HostingPlan.objects.filter(is_active=True) # Fetch only active plans
    return render(request, 'panel/list_hosting_plans.html', {'plans': plans})

# Handles the ordering process for a specific hosting plan.
# Requires user to be logged in.
# Takes plan_id from the URL to identify the selected plan.
@login_required
def order_hosting_plan_view(request, plan_id):
    plan = get_object_or_404(HostingPlan, id=plan_id, is_active=True) # Ensure plan exists and is active

    if request.method == 'POST':
        # Process submitted form data.
        form = OrderHostingForm(request.POST)
        if form.is_valid():
            domain_name = form.cleaned_data['domain_name']

            # Generate a secure password for the CyberPanel account
            # This password will be for the website user on CyberPanel
            website_password = secrets.token_urlsafe(16)

            # For CyberPanel username, a simple strategy is used:
            # Take the first 8 characters of the Django username (sanitized)
            # and append the first 4 characters of the domain name.
            # This strategy might need refinement for production to ensure uniqueness and meet CyberPanel's specific username requirements.
            base_cp_username = request.user.username.replace('.', '').replace('-', '')[:8]
            domain_prefix = domain_name.split('.')[0][:4] # First part of domain, e.g., 'yourdomain' from 'yourdomain.com'
            cyberpanel_username = f"{base_cp_username}{domain_prefix}"
            # Consider checking for username collisions or letting CyberPanel handle it if it provides feedback.

            # Instantiate the CyberPanel API client.
            api = CyberPanelAPI()
            # Call the API to create the website in CyberPanel.
            api_response = api.create_website(
                domain_name=domain_name,
                package_name=plan.cyberpanel_package_name,
                owner_username=cyberpanel_username, # This is the username for the website on CyberPanel
                owner_password=website_password,
                owner_email=request.user.email,
                # php_version can be a setting or part of the plan
            )

            # IMPORTANT: The following is a simulation placeholder as per subtask requirements.
            # In a live system, you MUST check the actual `api_response` from CyberPanel.
            # CyberPanel's API response structure for success/failure can vary.
            # Typically, a success might include {'createWebsiteStatus': 1} or similar.
            # A failure might include {'createWebsiteStatus': 0, 'error_message': 'Details...'}
            simulated_success = True # TODO: Replace with actual check of `api_response`

            if simulated_success:
                # If API call is considered successful, create a local CustomerService record.
                CustomerService.objects.create(
                    customer=request.user,
                    hosting_plan=plan,
                    domain_name=domain_name,
                    cyberpanel_username=cyberpanel_username # Store the generated/used CyberPanel username.
                                                            # Some APIs might return the actual username created, which would be better to store.
                    # is_active is True by default.
                )
                # The generated website_password is not stored locally by default for security.
                # Users would typically manage their password via CyberPanel or a password reset mechanism if provided.
                return redirect('order_success') # Redirect to a success confirmation page.
            else:
                # If API call fails, add an error message to the form to display to the user.
                # Extract a meaningful error from `api_response` if possible.
                error_message = api_response.get("error_message", api_response.get("error", "An unknown error occurred with the hosting provider."))
                form.add_error(None, f"Could not create website: {error_message}")

    else:
        # For GET request, display an empty order form.
        form = OrderHostingForm()

    return render(request, 'panel/order_hosting_plan.html', {'form': form, 'plan': plan})

# Displays a simple success message after an order is placed.
# Requires user to be logged in.
@login_required
def order_success_view(request):
    return render(request, 'panel/order_success.html')

# Displays a list of services owned by the currently logged-in user.
# Requires user to be logged in.
@login_required
def customer_services_view(request):
    services = CustomerService.objects.filter(customer=request.user) # Fetch services for the current user.

    from django.conf import settings # Import Django settings to fetch nameservers and FTP host.

    # Attempt to parse the FTP hostname from the CYBERPANEL_API_URL.
    # This is a basic parsing method and assumes a standard URL format (e.g., https://hostname:port/api/).
    # A more robust solution might involve a dedicated setting for the FTP hostname.
    ftp_hostname_from_api_url = ""
    try:
        # Example: CYBERPANEL_API_URL = 'https://your_cyberpanel_server_ip:8090/api/'
        api_url_parts = settings.CYBERPANEL_API_URL.split('/') # Splits into ['https:', '', 'hostname:port', 'api', '']
        if len(api_url_parts) > 2:
            ftp_hostname_from_api_url = api_url_parts[2].split(':')[0] # Extracts 'hostname' from 'hostname:port'
    except (AttributeError, IndexError):
        # AttributeError if CYBERPANEL_API_URL is not in settings.
        # IndexError if the URL format is unexpected.
        ftp_hostname_from_api_url = "your_server_ip_or_hostname" # Default fallback

    context = {
        'services': services,
        # Fetch nameservers from settings, with fallbacks if not defined.
        'primary_nameserver': getattr(settings, 'PRIMARY_NAMESERVER', 'ns1.example.com'),
        'secondary_nameserver': getattr(settings, 'SECONDARY_NAMESERVER', 'ns2.example.com'),
        # Fetch FTP hostname: use specific setting if available, else use parsed one, else fallback.
        'ftp_hostname': getattr(settings, 'CYBERPANEL_HOSTNAME', ftp_hostname_from_api_url)
    }
    return render(request, 'panel/customer_services.html', context)

# Root view for the 'panel' app.
# Redirects authenticated users to their service list ('customer_services').
# Redirects anonymous users to the hosting plan list ('list_hosting_plans').
def panel_index_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('customer_services'))
    else:
        # For anonymous users, it's more logical to show plans or login/register.
        # list_hosting_plans is a good public entry point.
        return redirect(reverse('list_hosting_plans'))
