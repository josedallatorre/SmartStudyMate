from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
import asyncio 
import os 
from urllib.request import urlretrieve
from os import open


async def me():

    credential = InteractiveBrowserCredential()
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credential, scopes)
    me = await graph_client.me.get()
    teams = await graph_client.me.joined_teams.get()
    print(teams)
    #group_id = input("\n group id? \n")
    drive = await graph_client.groups.by_group_id(group_id).drive.get()
    print(drive)
    #drive_id = input("\ndrive id? \n")
    root = await graph_client.drives.by_drive_id(drive_id).root.get()
    print(root)
    #drive_item_id= input("\n drive item id? \n")
    childrens = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(drive_item_id).children.get()
    print(childrens)
    #content_id = input("\n content id?")
    query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(
            #select=['id', "@microsoft.graph.downloadUrl"]
            select=['id','name']
        )
    request_config = ChildrenRequestBuilder.ChildrenRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

    childrens = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(drive_item_id).children.get(request_config)
    print(childrens)
    #content = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).content.get()
    #print("\n content:"+str(content))
    """
    urlretrieve(url_to_retrieve)
    url = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
    response = requests.get(url, stream=True)
    with requests.get(url, stream=True) as response:
    # ...
    with open("WDI_CSV.zip", mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)
    """


    
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/root/children
    
    #get children of "COPPOLA" folder
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVV7DNQJHIKYC4BFLBZOKORXABDCM/children/

    #get a content
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVVZS27LN2OKLGVBLQXK5ESUXJGK4/content


if __name__ == "__main__":
    asyncio.run(me())