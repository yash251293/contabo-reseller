import requests
from django.conf import settings
import json

# This class provides a Python interface to the CyberPanel API.
# It handles making requests to various API endpoints for managing websites, users, etc.
class CyberPanelAPI:
    def __init__(self):
        # Initialize with API connection details from Django settings.
        self.base_url = settings.CYBERPANEL_API_URL
        self.admin_username = settings.CYBERPANEL_ADMIN_USERNAME
        self.admin_password = settings.CYBERPANEL_ADMIN_PASSWORD

    def _make_request(self, endpoint, data):
        """
        Helper function to make POST requests to the CyberPanel API.
        Handles URL construction, adding authentication, sending the request,
        and basic error/response processing.

        Args:
            endpoint (str): The API endpoint path (e.g., "submitUserCreation").
            data (dict): A dictionary containing the data to be sent in the request body.

        Returns:
            dict: The JSON response from the API, or a dictionary with an error message.
        """
        # Construct the full API URL.
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        headers = {
            'Content-Type': 'application/json', # CyberPanel API typically expects JSON.
        }

        # Add admin credentials to every request payload.
        # This is a common authentication pattern for CyberPanel's API.
        data['adminUser'] = self.admin_username
        data['adminPass'] = self.admin_password

        try:
            # Make the POST request.
            # `verify=False` is used to bypass SSL certificate verification, often needed for self-signed certs in dev.
            # WARNING: For production, ensure proper SSL certificates or use `verify=True` with a valid CA bundle.
            response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

            # Raise an HTTPError if the HTTP request returned an unsuccessful status code (4xx or 5xx).
            response.raise_for_status()

            # Attempt to parse the JSON response.
            # Some CyberPanel API responses might not be JSON, or might be empty on success.
            try:
                return response.json()
            except json.JSONDecodeError:
                # If response is not JSON, return its raw text content, which might contain success/error messages.
                return {"raw_response": response.text, "status_code": response.status_code}

        except requests.exceptions.RequestException as e:
            # Handle network errors, timeouts, etc.
            # In a production app, this should be logged more robustly.
            print(f"Error connecting to CyberPanel API endpoint {endpoint}: {e}")
            # Return a structured error message.
            return {"error": str(e), "status_code": response.status_code if 'response' in locals() and hasattr(response, 'status_code') else None}

    # Note: The 'login' function is often not explicitly needed if adminUser/adminPass are sent with each request.
    # Some API versions or specific endpoints might require a session token obtained via a login call.
    # This is a placeholder if such a mechanism is needed.
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
        Creates a new website (hosting account) in CyberPanel.
        Corresponds to CyberPanel's `/api/submitUserCreation` endpoint.

        Args:
            domain_name (str): The domain for the new website.
            package_name (str): The name of the hosting package in CyberPanel.
            owner_username (str): The username for the website owner on CyberPanel.
            owner_email (str): The email for the website owner.
            owner_password (str): The password for the website owner.
            php_version (str, optional): The desired PHP version (e.g., "PHP 7.4"). Defaults to "PHP 7.4".

        Returns:
            dict: The API response.
        """
        data = {
            "websiteName": domain_name,
            "packageName": package_name,
            "username": owner_username,
            "email": owner_email,
            "password": owner_password,
            "php": php_version,
            # Other optional parameters for submitUserCreation can be added here,
            # e.g., acl, securityLevel, mailChild, etc., based on CyberPanel API docs.
        }
        return self._make_request("submitUserCreation", data) # API endpoint for creating websites.

    def suspend_website(self, domain_name):
        """
        Suspends an existing website in CyberPanel.
        Corresponds to CyberPanel's `/api/changeWebsiteStatus` endpoint with status 0.

        Args:
            domain_name (str): The domain of the website to suspend.

        Returns:
            dict: The API response.
        """
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
        Unsuspends a previously suspended website in CyberPanel.
        Corresponds to CyberPanel's `/api/changeWebsiteStatus` endpoint with status 1.

        Args:
            domain_name (str): The domain of the website to unsuspend.

        Returns:
            dict: The API response.
        """
        # CyberPanel API endpoint for unsuspending a website.
        # Common endpoint: /api/changeWebsiteStatus (or similar)
        # Requires websiteName and status (0 for suspend, 1 for unsuspend)
        data = {
            "websiteName": domain_name,
            "status": 1  # 1 for Unsuspend (or Resume)
        }
        return self._make_request("changeWebsiteStatus", data) # API endpoint for changing website status.

    def delete_website(self, domain_name):
        """
        Deletes an existing website from CyberPanel.
        Corresponds to CyberPanel's `/api/deleteWebsite` endpoint.

        Args:
            domain_name (str): The domain of the website to delete.

        Returns:
            dict: The API response.
        """
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
        Retrieves a list of available hosting packages defined in CyberPanel.
        Corresponds to CyberPanel's `/api/getPackage` endpoint (or similar, e.g., `getPackages`).
        Note: This specific endpoint might not require `adminUser`/`adminPass` in the payload,
        but our `_make_request` adds them by default. This is usually fine for POST-based APIs.
        If it were a GET endpoint or had different auth, `_make_request` would need adjustment
        or a separate helper for such cases.
        """
        data = {} # Typically, listing packages might not require a request body.
                  # If specific filters are needed, they would be added here.
        return self._make_request("getPackage", data) # API endpoint for listing packages.

# Example usage (for manual testing or reference, not part of the running application flow here):
# if __name__ == '__main__':
#     # This section would only run if the script is executed directly (e.g., python cyberpanel_api.py)
#     # It requires Django settings to be configured, which is not standard for direct script execution
#     # without `manage.py` or `django.setup()`.
# from django.conf import settings as django_settings
# django_settings.configure(
# CYBERPANEL_API_URL='https://your_cyberpanel_server_ip:8090/api/',
# CYBERPANEL_ADMIN_USERNAME='your_admin_user',
# CYBERPANEL_ADMIN_PASSWORD='your_admin_password'
# )
#     api = CyberPanelAPI()
# print(api.list_packages())
# print(api.create_website("testdomain123.com", "Default", "testuser", "test@testdomain123.com", "aVeryStrongPassword123!"))
