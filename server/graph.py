from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
from msgraph.generated.drives.item.items.item.drive_item_item_request_builder import DriveItemItemRequestBuilder
import asyncio 
from builtins import open
import aiohttp
import time
import os
from dotenv import load_dotenv
load_dotenv()

class Graph:

    credential: InteractiveBrowserCredential
    graph_client: GraphServiceClient

    def __init__(self):
        self.credential = InteractiveBrowserCredential()
        self.scopes = ['https://graph.microsoft.com/.default']
        self.graph_client = GraphServiceClient(self.credential, scopes=self.scopes) # type: ignore

    def authenticate(self):
        return self.credential.get_token('https://graph.microsoft.com/.default')

    async def me(self):
        me = await self.graph_client.me.get()
        return me

    async def get_joined_teams(self):
        teams = await self.graph_client.me.joined_teams.get()
        return teams
    
    """
    #group_id = input("\n group id? \n")
    drive = await graph_client.groups.by_group_id(group_id).drive.get()
    print(drive)
    #drive_id = input("\ndrive id? \n")
    root = await graph_client.drives.by_drive_id(drive_id).root.get()
    print(root)
    #drive_item_id= input("\n drive item id? \n")
    childrens = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(drive_item_id).children.get()
    print("\n childrens:\n"+str(childrens)+"\n")
    #content_id = input("\n content id?")
    query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(
            #select=['id', "@microsoft.graph.downloadUrl"]
            select=['id','name']
        )
    request_config = ChildrenRequestBuilder.ChildrenRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

    childrens = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(drive_item_id).children.get(request_config)
    childrens_id =[]
    for children in childrens.value:
        print("\n children:\n"+str(children)+"\n")
        childrens_id.append(children.id)

    #content_id = '01GQ6WVV3KMPECR3QSTFAIRP7WNC6IMAWT'
    #content_id = '01GQ6WVV2O6XSJUPED4NH3QSCKWXJFFC7P'
    
    query_params = DriveItemItemRequestBuilder.DriveItemItemRequestBuilderGetQueryParameters(
		select = ["id","@microsoft.graph.downloadUrl","name"],
    )

    request_configuration = DriveItemItemRequestBuilder.DriveItemItemRequestBuilderGetRequestConfiguration(
    query_parameters = query_params,
    )
    urls = []
    for content_id in childrens_id:
        content = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).get()
        url_to_retrieve = str(content.additional_data.get('@microsoft.graph.downloadUrl'))
        urls.append(url_to_retrieve)
        print("\n content:\n"+str(content)+"\n")
        print("\n url to retrieve:\n"+str(url_to_retrieve)+"\n")
        content = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).get()
        print("\n content:\n"+str(content)+"\n")
        #content = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).content.get()



    #print(urlretrieve(url_to_retrieve, "file.mp4"))
    
    #url = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
    #response = requests.get(url_to_retrieve, stream=True)
    #print(response.)
    start_time = time.time()    
    print(urls)
    n=3
    subarrays = []
    for i in range(0, len(urls), 3):
        subarrays.append(urls[i:i+3])
    for a in subarrays:
        tasks = [download_file(url) for url in a]
        await asyncio.gather(*tasks)
    print('download done')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("\nAll tasks completed in {:.2f} seconds".format(elapsed_time))
    # All tasks completed in 994.13 seconds for TASSO folder


   async def download_file(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    resp ={"error": f"server returned {response.status}"}
                else:
                    if "content-disposition" in response.headers:
                        header = response.headers["content-disposition"]
                        filename = header.split("filename=")[1]
                        filename = filename.replace("\"", "") # replace front and trailing "
                        print(filename)
                    else:
                        filename = url.split("/")[-1]
                    with open(filename, mode="wb") as file:
                        while True:
                            chunk = await response.content.read()
                            if not chunk:
                                break
                            file.write(chunk)
                        print(f"Downloaded file {filename}")
        except asyncio.TimeoutError:
            print(f"timeout error on {url}")
    
"""
#if __name__ == "__main__":
#    asyncio.run(me())