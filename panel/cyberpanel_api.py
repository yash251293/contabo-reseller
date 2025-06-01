import requests
from django.conf import settings
import json

class CyberPanelAPI:
    def __init__(self):
        self.base_url = settings.CYBERPANEL_API_URL
        self.admin_username = settings.CYBERPANEL_ADMIN_USERNAME
        self.admin_password = settings.CYBERPANEL_ADMIN_PASSWORD

    def _make_request(self, endpoint, data):
        """
        Helper function to make POST requests to the CyberPanel API.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            'Content-Type': 'application/json',
        }
        # Add admin credentials to the data payload for CyberPanel API
        data['adminUser'] = self.admin_username
        data['adminPass'] = self.admin_password

        try:
            response = requests.post(url, data=json.dumps(data), headers=headers, verify=False) # verify=False for self-signed certs, use with caution
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            # CyberPanel API might return non-JSON success messages or error details
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"raw_response": response.text}

        except requests.exceptions.RequestException as e:
            # Log the error or handle it as needed
            print(f"Error connecting to CyberPanel API: {e}")
            # In a real app, you might want to raise a custom exception
            return {"error": str(e), "status_code": response.status_code if 'response' in locals() else None}

    # Placeholder functions for CyberPanel API actions
    # These will be based on /api/submitUserCreation, /api/deleteWebsite etc.

    def login(self):
        """
        Authenticates with CyberPanel.
        Based on /api/verifyLogin or /api/loginAPI.
        For now, we assume credentials are passed directly in each request if needed.
        This function might be used if a session token is required by some endpoints.
        """
        # Example: /api/verifyLogin
        # data = {"username": self.admin_username, "password": self.admin_password}
        # return self._make_request("verifyLogin", data)
        # For submitUserCreation, login is implicit via adminUser/adminPass
        pass

    def create_website(self, domain_name, package_name, owner_username, owner_email, owner_password, php_version="PHP 7.4"):
        """
        Creates a new website/hosting account in CyberPanel.
        Based on /api/submitUserCreation.
        """
        data = {
            "websiteName": domain_name,
            "packageName": package_name,
            "username": owner_username,
            "email": owner_email,
            "password": owner_password,
            "php": php_version,
            # Add other parameters as required by CyberPanel's submitUserCreation endpoint
            # e.g., acl, securityLevel, etc.
        }
        return self._make_request("submitUserCreation", data)

    def suspend_website(self, domain_name):
        """
        Suspends a website in CyberPanel.
        Endpoint needs to be verified, e.g., /api/users/suspendUser or similar.
        For now, assuming an endpoint and typical parameters.
        """
        # CyberPanel API endpoint for suspending a website.
        # Common endpoint: /api/changeWebsiteStatus (or similar)
        # Requires websiteName and status (0 for suspend, 1 for unsuspend)
        data = {
            "websiteName": domain_name,
            "status": 0  # 0 for Suspend
        }
        return self._make_request("changeWebsiteStatus", data)

    def unsuspend_website(self, domain_name):
        """
        Unsuspends a website in CyberPanel.
        Endpoint needs to be verified, e.g., /api/users/unsuspendUser or similar.
        """
        # CyberPanel API endpoint for unsuspending a website.
        # Common endpoint: /api/changeWebsiteStatus (or similar)
        # Requires websiteName and status (0 for suspend, 1 for unsuspend)
        data = {
            "websiteName": domain_name,
            "status": 1  # 1 for Unsuspend
        }
        return self._make_request("changeWebsiteStatus", data)

    def delete_website(self, domain_name):
        """
        Deletes a website from CyberPanel.
        Based on /api/deleteWebsite.
        """
        data = {
            "websiteName": domain_name,
        }
        return self._make_request("deleteWebsite", data)

    def list_packages(self):
        """
        Retrieves available hosting packages from CyberPanel.
        Based on /api/getPackage or similar.
        """
        # This endpoint usually doesn't require adminUser/adminPass in the payload itself
        # but rather as part of a general authenticated session or if the endpoint is protected.
        # For simplicity, our _make_request adds them, which might be ignored or cause issues
        # for GET-like endpoints if they exist. CyberPanel API is heavily POST based.
        data = {} # May not need a body, or might need specific parameters
        return self._make_request("getPackage", data)

# Example of how to use it (for testing purposes, not for live calls in this subtask)
# if __name__ == '__main__':
# from django.conf import settings as django_settings
# django_settings.configure(
# CYBERPANEL_API_URL='https://your_cyberpanel_server_ip:8090/api/',
# CYBERPANEL_ADMIN_USERNAME='your_admin_user',
# CYBERPANEL_ADMIN_PASSWORD='your_admin_password'
# )
#     api = CyberPanelAPI()
# print(api.list_packages())
# print(api.create_website("testdomain123.com", "Default", "testuser", "test@testdomain123.com", "aVeryStrongPassword123!"))
