from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder

from msgraph.generated.drives.item.items.item.drive_item_item_request_builder import DriveItemItemRequestBuilder
import asyncio 
from urllib.request import urlretrieve
from builtins import open
import requests

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
    #content_id = '01GQ6WVV3KMPECR3QSTFAIRP7WNC6IMAWT'
    content_id = '01GQ6WVV2O6XSJUPED4NH3QSCKWXJFFC7P'
    
    query_params = DriveItemItemRequestBuilder.DriveItemItemRequestBuilderGetQueryParameters(
		select = ["id","@microsoft.graph.downloadUrl","name"],
    )

    request_configuration = DriveItemItemRequestBuilder.DriveItemItemRequestBuilderGetRequestConfiguration(
    query_parameters = query_params,
    )

    content = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).get()
    url_to_retrieve = str(content.additional_data.get('@microsoft.graph.downloadUrl'))

    content = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).get()
    print("\n content:\n"+str(content))
    #content = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).content.get()



    print(urlretrieve(url_to_retrieve, "file.mp4"))
    
    #url = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
    #response = requests.get(url_to_retrieve, stream=True)
    #print(response.)
    with requests.get(url_to_retrieve, stream=True) as response:
        with open("file_request.mp4", "wb") as file:
            for chunk in response.iter_content(chunk_size=10 * 1024):
                file.write(chunk)

    
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/root/children
    
    #get children of "COPPOLA" folder
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVV7DNQJHIKYC4BFLBZOKORXABDCM/children/

    #get a content
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVVZS27LN2OKLGVBLQXK5ESUXJGK4/content


if __name__ == "__main__":
    asyncio.run(me())