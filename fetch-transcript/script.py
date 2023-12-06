import os 
import asyncio
import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient

credential = ClientSecretCredential(
    'tenant_id',
    'client_id',
    'client_secret'
)
groupId = os.getenv('groupID')

graph_client = GraphServiceClient(credentials, scopes)

async def get_group():
    result = await graph_client.groups.by_group_id(groupId).get()
    print(result)
asyncio.run(get_group)

scopes = ['User.Read']

# Multi-tenant apps can use "common",
# single-tenant apps must use the tenant ID from the Azure portal
tenant_id = 'common'

# Values from app registration
client_id = 'YOUR_CLIENT_ID'
redirect_uri = 'http://localhost:8000'

# azure.identity
credential = InteractiveBrowserCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    redirect_uri=redirect_uri)

graph_client = GraphServiceClient(credential, scopes)