import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = "0c91214b-ac91-4e05-a828-ded6e4f77c73" # Application (client) ID of app registration

# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
if not CLIENT_SECRET:
    raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = "https://login.microsoftonline.com/organizations"  # For multi-tenant app
# AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
#ENDPOINT2 = 'https://graph.microsoft.com/v1.0/users/4c675eae-8304-4358-b9f7-d4480cfc798b/onlineMeetings/AAMkAGFjNmZhMDRiLTU1OGEtNGM3OC05MGFlLTllODk0OWYzNjFmYQBGAAAAAAD3p0rX5oaDSp0zUxLz21soBwBHgbmfciJ1Q6vNMjBkuvckAAAAAAENAABHgbmfciJ1Q6vNMjBkuvckAABrzcrQAAA=/transcripts'  # This resource requires no admin consent
ENDPOINT2 = 'https://graph.microsoft.com/v1.0/me/joinedTeams'
ENDPOINT = 'https://graph.microsoft.com/v1.0/me/'

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.Read", "Team.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
