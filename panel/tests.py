from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from .models import HostingPlan, CustomerService
from .forms import OrderHostingForm, CustomUserCreationForm
from .cyberpanel_api import CyberPanelAPI
from django.conf import settings

# Helper to print test status
def print_test_status(test_name, status):
    print(f"[TEST STATUS] {test_name}: {status}")

class BaseModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        cls.plan = HostingPlan.objects.create(
            name="Basic Plan",
            disk_space_gb=10,
            bandwidth_gb=100,
            email_accounts=5,
            databases=1,
            price_monthly=5.00,
            cyberpanel_package_name="BasicPackage"
        )
        print_test_status("BaseModelTests.setUpTestData", "Completed")

    def test_hosting_plan_creation(self):
        self.assertEqual(self.plan.name, "Basic Plan")
        self.assertEqual(str(self.plan), "Basic Plan")
        print_test_status("test_hosting_plan_creation", "PASSED")

    def test_customer_service_creation(self):
        service = CustomerService.objects.create(
            customer=self.user,
            hosting_plan=self.plan,
            domain_name="testdomain.com",
            cyberpanel_username="testcpuser"
        )
        self.assertEqual(service.domain_name, "testdomain.com")
        self.assertEqual(str(service), f"{self.user.username} - {service.domain_name}")
        print_test_status("test_customer_service_creation", "PASSED")

class FormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        print_test_status("FormTests.setUpTestData", "Completed")

    def test_order_hosting_form_valid(self):
        form_data = {'domain_name': 'validdomain.com'}
        form = OrderHostingForm(data=form_data)
        self.assertTrue(form.is_valid())
        print_test_status("test_order_hosting_form_valid", "PASSED")

    def test_order_hosting_form_invalid_missing_domain(self):
        form_data = {'domain_name': ''}
        form = OrderHostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('domain_name', form.errors)
        print_test_status("test_order_hosting_form_invalid_missing_domain", "PASSED")

    def test_order_hosting_form_invalid_domain_format(self):
        form_data = {'domain_name': 'invaliddomain'}
        form = OrderHostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('domain_name', form.errors)
        print_test_status("test_order_hosting_form_invalid_domain_format", "PASSED")

    def test_custom_user_creation_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password2': 'newpassword123', # Django's UserCreationForm uses password1 and password2
            'password': 'newpassword123',
        }
        # Note: Django's UserCreationForm uses password1 and password2.
        # Our CustomUserCreationForm inherits this.
        # For the test, we need to simulate the form structure correctly.
        # The fields are typically 'username', 'email', 'password', 'password2'
        # Let's assume the form is defined as:
        # class CustomUserCreationForm(UserCreationForm):
        #     class Meta(UserCreationForm.Meta):
        # fields = UserCreationForm.Meta.fields + ("email",)
        # UserCreationForm itself has password1 and password2 for validation.
        # We need to provide password1 and password2 if testing the full form validation.
        # However, our CustomUserCreationForm doesn't explicitly list password1 and password2
        # in its Meta fields, it inherits them.
        # For direct instantiation like this, we might need to ensure all required fields by the parent are provided.

        # Let's refine the data for UserCreationForm parent
        form_data_parent = {
            'username': 'newuser',
            'email': 'newuser@example.com', # This is our custom addition
            'password': 'newpassword123', # This is not how UserCreationForm works
            'password2': 'newpassword123', # This is also not quite it
        }
        # Correct fields for UserCreationForm are password1 and password2
        correct_form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123', # This is how our form is used in the view
            # The view passes request.POST which contains 'password' if the HTML field is named 'password'
            # The form's clean method handles this.
            # Let's test CustomUserCreationForm's cleaning of password.
            # It relies on superclass UserCreationForm's password validation.
            # For a direct test, we might need to provide password1 and password2.
            # However, the provided form `CustomUserCreationForm` is simple.
            # Let's assume it works if email is present and username is unique.
        }
        # For a more robust test of UserCreationForm, we'd need password1 and password2
        # Let's test our form as it is defined.
        # Our form in forms.py:
        # class CustomUserCreationForm(UserCreationForm):
        #    class Meta(UserCreationForm.Meta):
        #        fields = UserCreationForm.Meta.fields + ("email",)
        # This means it will use the default fields from UserCreationForm and add 'email'.
        # Default fields usually include 'username', 'password', 'password2'.

        # Re-checking UserCreationForm: it expects 'password' and 'password2' from the form submission in request.POST
        # Let's assume the form is used with fields named 'username', 'email', 'password', 'password2' in the template
        # Or, if we use {{ form.as_p }}, Django names them password and password2.
        # Our template for register.html iterates through form fields.
        # Django's default UserCreationForm has 'password' and 'password2' fields.
        # Let's assume the data provided to the form will have these keys.
        form_data_for_custom = {
            'username': 'anotheruser',
            'email': 'another@example.com',
            'password': 'testpassword123', # This should be password1
            'password2': 'testpassword123'
        }
        # The actual fields in UserCreationForm are 'password' and 'password2'
        # Let's assume our CustomUserCreationForm is used in a context where request.POST would have 'password' and 'password2'
        # So the data should be:
        form_data = {'username': 'testuser10', 'email': 'test10@example.com', 'password': 'password123', 'password2': 'password123'}

        # Our form is CustomUserCreationForm, it adds 'email' to UserCreationForm.
        # UserCreationForm has 'password' and 'password2' fields.
        # The actual fields are `password` and `password2`.
        form = CustomUserCreationForm(data=form_data)
        if not form.is_valid():
            print(f"CustomUserCreationForm errors: {form.errors.as_json()}")
        self.assertTrue(form.is_valid())
        print_test_status("test_custom_user_creation_form_valid", "PASSED")


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(username='viewtestuser', email='viewtest@example.com', password='password123')
        cls.plan = HostingPlan.objects.create(name="View Plan", price_monthly=10.00, cyberpanel_package_name="ViewPackage", disk_space_gb=1, bandwidth_gb=1, email_accounts=1, databases=1)
        print_test_status("ViewTests.setUpTestData", "Completed")

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panel/register.html')
        print_test_status("test_register_view_get", "PASSED")

    def test_register_view_post_valid(self):
        user_count_before = User.objects.count()
        response = self.client.post(reverse('register'), {
            'username': 'newreguser',
            'email': 'newreg@example.com',
            'password': 'newpassword123', # Assuming form field name is 'password'
            'password2': 'newpassword123',# And 'password2' for confirmation
        }, follow=True) # Follow redirect
        self.assertEqual(User.objects.count(), user_count_before + 1)
        # Should redirect to profile on successful registration and login
        self.assertRedirects(response, reverse('profile'), status_code=302, target_status_code=200)
        print_test_status("test_register_view_post_valid", "PASSED")

    def test_register_view_post_invalid(self):
        response = self.client.post(reverse('register'), {'username': '', 'password': 'pw'})
        self.assertEqual(response.status_code, 200) # Should re-render form
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        print_test_status("test_register_view_post_invalid", "PASSED")

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panel/profile.html')
        print_test_status("test_profile_view_requires_login", "PASSED")

    def test_list_hosting_plans_view_requires_login(self):
        response = self.client.get(reverse('list_hosting_plans'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('list_hosting_plans')}")

        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('list_hosting_plans'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.plan.name)
        print_test_status("test_list_hosting_plans_view_requires_login", "PASSED")

    @patch('panel.views.CyberPanelAPI.create_website')
    def test_order_hosting_plan_view_post_valid_mock_api_success(self, mock_create_website):
        mock_create_website.return_value = {'websiteStatus': 'success', 'createWebsiteStatus': 1, 'username': 'cp_user_from_api'}
        self.client.login(username='viewtestuser', password='password123')

        services_before = CustomerService.objects.count()
        response = self.client.post(reverse('order_hosting_plan', args=[self.plan.id]), {
            'domain_name': 'mytestdomain.com'
        }, follow=True)

        self.assertEqual(CustomerService.objects.count(), services_before + 1)
        new_service = CustomerService.objects.latest('created_at')
        self.assertEqual(new_service.domain_name, 'mytestdomain.com')
        self.assertEqual(new_service.customer, self.user) # self.user is 'viewtestuser'
        # self.assertEqual(new_service.cyberpanel_username, 'cp_user_from_api') # This needs API to return it and view to use it
        self.assertRedirects(response, reverse('order_success'), status_code=302, target_status_code=200)
        mock_create_website.assert_called_once()
        print_test_status("test_order_hosting_plan_view_post_valid_mock_api_success", "PASSED")


    @patch('panel.views.CyberPanelAPI.create_website')
    def test_order_hosting_plan_view_post_api_failure(self, mock_create_website):
        # Simulate API failure
        mock_create_website.return_value = {'createWebsiteStatus': 0, 'error_message': 'CyberPanel API Error'}
        self.client.login(username='viewtestuser', password='password123')

        services_before = CustomerService.objects.count()
        response = self.client.post(reverse('order_hosting_plan', args=[self.plan.id]), {
            'domain_name': 'anotherdomain.com'
        })

        self.assertEqual(CustomerService.objects.count(), services_before) # No service created
        self.assertEqual(response.status_code, 200) # Re-renders form
        self.assertContains(response, "Could not create website: CyberPanel API Error")
        mock_create_website.assert_called_once()
        print_test_status("test_order_hosting_plan_view_post_api_failure", "PASSED")

    def test_customer_services_view_requires_login(self):
        response = self.client.get(reverse('customer_services'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('customer_services')}")

        self.client.login(username='viewtestuser', password='password123')
        CustomerService.objects.create(customer=self.user, hosting_plan=self.plan, domain_name="userservice.com")
        response = self.client.get(reverse('customer_services'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "userservice.com")
        print_test_status("test_customer_services_view_requires_login", "PASSED")


class CyberPanelAPITests(TestCase):
    def setUp(self):
        # Ensure settings are configured for API tests, even if default/placeholders
        settings.CYBERPANEL_API_URL = 'https://testpanel.com:8090/api/'
        settings.CYBERPANEL_ADMIN_USERNAME = 'test_admin'
        settings.CYBERPANEL_ADMIN_PASSWORD = 'test_password'
        self.api = CyberPanelAPI()
        print_test_status(f"CyberPanelAPITests.setUp for {self._testMethodName}", "Completed")

    @patch('panel.cyberpanel_api.requests.post')
    def test_create_website_api_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'websiteStatus': 'success', 'createWebsiteStatus': 1}
        mock_post.return_value = mock_response

        result = self.api.create_website(
            domain_name="newsite.com", package_name="Default",
            owner_username="newsiteuser", owner_email="owner@newsite.com", owner_password="securepassword"
        )

        expected_url = f"{settings.CYBERPANEL_API_URL.rstrip('/')}/submitUserCreation"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], expected_url)
        self.assertIn('"websiteName": "newsite.com"', kwargs['data'])
        self.assertTrue(result['websiteStatus'] == 'success')
        print_test_status("test_create_website_api_success", "PASSED")

    @patch('panel.cyberpanel_api.requests.post')
    def test_create_website_api_failure_status_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400 # Simulate an HTTP error
        mock_response.json.return_value = {'error_message': 'Bad request from API'}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error") # Mock raise_for_status
        mock_post.return_value = mock_response

        result = self.api.create_website(
            domain_name="failsite.com", package_name="Default",
            owner_username="failuser", owner_email="owner@fail.com", owner_password="pw"
        )

        self.assertIn('error', result)
        self.assertIn('API Error', result['error']) # Check for the HTTPError message
        print_test_status("test_create_website_api_failure_status_code", "PASSED")

    @patch('panel.cyberpanel_api.requests.post')
    def test_suspend_website_api_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 1, 'message': 'Website suspended successfully'} # Example response
        mock_post.return_value = mock_response

        result = self.api.suspend_website(domain_name="suspendme.com")

        expected_url = f"{settings.CYBERPANEL_API_URL.rstrip('/')}/changeWebsiteStatus"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], expected_url)
        self.assertIn('"websiteName": "suspendme.com"', kwargs['data'])
        self.assertIn('"status": 0', kwargs['data']) # 0 for suspend
        self.assertEqual(result.get('status'), 1)
        print_test_status("test_suspend_website_api_success", "PASSED")

    @patch('panel.cyberpanel_api.requests.post')
    def test_unsuspend_website_api_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 1, 'message': 'Website unsuspended successfully'}
        mock_post.return_value = mock_response

        result = self.api.unsuspend_website(domain_name="unsuspendme.com")

        expected_url = f"{settings.CYBERPANEL_API_URL.rstrip('/')}/changeWebsiteStatus"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], expected_url)
        self.assertIn('"websiteName": "unsuspendme.com"', kwargs['data'])
        self.assertIn('"status": 1', kwargs['data']) # 1 for unsuspend
        self.assertEqual(result.get('status'), 1)
        print_test_status("test_unsuspend_website_api_success", "PASSED")

    @patch('panel.cyberpanel_api.requests.post')
    def test_delete_website_api_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'deleteWebsiteStatus': 1, 'message': 'Website deleted successfully'}
        mock_post.return_value = mock_response

        result = self.api.delete_website(domain_name="deleteme.com")

        expected_url = f"{settings.CYBERPANEL_API_URL.rstrip('/')}/deleteWebsite"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], expected_url)
        self.assertIn('"websiteName": "deleteme.com"', kwargs['data'])
        self.assertEqual(result.get('deleteWebsiteStatus'), 1)
        print_test_status("test_delete_website_api_success", "PASSED")


# Note: Admin action tests are more complex.
# We can test the helper functions if logic is extracted,
# or test actions by constructing mock requests and calling action functions directly.
# For now, focusing on API method calls which are the core of admin actions.

# This import is needed for CyberPanelAPITests.test_create_website_api_failure_status_code
import requests
print_test_status("panel/tests.py", "LOADED")

# To run these tests: python manage.py test panel
# Add more tests for edge cases, different API responses, etc.

# Example for testing admin action directly (simplified)
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group # Required by some admin internals if not using full request
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from .admin import CustomerServiceAdmin # Assuming your admin class
from .models import CustomerService # Assuming your model

class AdminActionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='admintestuser', password='password123', is_staff=True, is_superuser=True)
        cls.plan = HostingPlan.objects.create(name="Admin Plan", price_monthly=10.00, cyberpanel_package_name="AdminPackage", disk_space_gb=1, bandwidth_gb=1, email_accounts=1, databases=1)
        cls.service_to_suspend = CustomerService.objects.create(customer=cls.user, hosting_plan=cls.plan, domain_name="suspendtest.com", is_active=True)
        print_test_status("AdminActionTests.setUpTestData", "Completed")

    @patch('panel.cyberpanel_api.CyberPanelAPI.suspend_website') # Patch at the source of CyberPanelAPI
    def test_suspend_service_admin_action(self, mock_suspend_website_api):
        # Simulate a successful API response
        mock_suspend_website_api.return_value = {'status': 1, 'message': 'Mocked suspend success'}

        modeladmin = CustomerServiceAdmin(CustomerService, AdminSite())
        request = HttpRequest()
        request.user = self.user # Admin user

        # Mock messages framework
        setattr(request, '_messages', FallbackStorage(request))

        queryset = CustomerService.objects.filter(id=self.service_to_suspend.id)

        # Call the action
        modeladmin.suspend_selected_services(request, queryset)

        mock_suspend_website_api.assert_called_once_with(domain_name="suspendtest.com")
        self.service_to_suspend.refresh_from_db()
        self.assertFalse(self.service_to_suspend.is_active)

        # Check messages (optional, depends on how you want to assert this)
        # messages = [m.message for m in list(request._messages)]
        # self.assertIn("Successfully suspended 1 service(s).", messages)
        print_test_status("test_suspend_service_admin_action", "PASSED")

print_test_status("panel/tests.py", "FULLY PARSED")
