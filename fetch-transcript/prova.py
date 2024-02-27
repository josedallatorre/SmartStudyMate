from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient
import asyncio 

async def me():
    credential = InteractiveBrowserCredential()
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credential, scopes)
    me = await graph_client.me.get()
    if me:
        print(me)    
if __name__ == "__main__":
    asyncio.run(me())