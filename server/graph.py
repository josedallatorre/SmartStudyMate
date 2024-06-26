from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
from msgraph.generated.drives.item.items.item.drive_item_item_request_builder import DriveItemItemRequestBuilder
import asyncio 
from builtins import open
import aiohttp
import time
import os
from content import Content
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
    
    async def get_drive(self, group_id):
        #group_id = input("\n group id? \n")
        drive = await self.graph_client.groups.by_group_id(group_id).drive.get()
        return drive
    
    async def get_drive_root(self, drive_id):
        drive_id2= 'b!KZ7JAPsh4EOfSWEwf8S5RwCM8BJW3BNCv3oZoxQUSsoR_gJ69LB5RavzlRzxKr_0'
        #drive_id = input("\ndrive id? \n")
        root = await self.graph_client.drives.by_drive_id(drive_id2).root.get()
        print(root)
        return root
    
    async def get_drive_childrens(self, drive_id, drive_item_id):
        #drive_item_id= input("\n drive item id? \n")
        childrens = await self.graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(drive_item_id).children.get()
        print("\n childrens:\n"+str(childrens)+"\n")
        return childrens


    async def get_drive_childrens_opt(self, drive_id, drive_item_id):
        #content_id = input("\n content id?")
        query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(
                #select=['id', "@microsoft.graph.downloadUrl"]
                select=['id','name']
            )
        request_config = ChildrenRequestBuilder.ChildrenRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )

        childrens = await self.graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(drive_item_id).children.get(request_config)
        childrens_id =[]
        for children in childrens.value:
            print("\n children:\n"+str(children)+"\n")
            childrens_id.append(children.id)
        return childrens, childrens_id

    #content_id = '01GQ6WVV3KMPECR3QSTFAIRP7WNC6IMAWT'
    #content_id = '01GQ6WVV2O6XSJUPED4NH3QSCKWXJFFC7P'
    async def get_children_id(self, drive_id, childrens_id):
        query_params = DriveItemItemRequestBuilder.DriveItemItemRequestBuilderGetQueryParameters(
            select = ["id","@microsoft.graph.downloadUrl","name"],
        )

        request_configuration = DriveItemItemRequestBuilder.DriveItemItemRequestBuilderGetRequestConfiguration(
        query_parameters = query_params,
        )
        contents = []
        for content_id in childrens_id:
            content = await self.graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(content_id).get()
            url_to_retrieve = str(content.additional_data.get('@microsoft.graph.downloadUrl'))
            c = Content()
            c.url = url_to_retrieve
            c.name = content.name
            c.id = content.id
            contents.append(c)
            print("\n content:\n"+str(content)+"\n")
            print("\n c.url:\n"+str(c.url)+"\n")
            print("\n c.name:\n"+str(c.name)+"\n")
            print("\n c.id:\n"+str(c.id)+"\n")
        return contents

   
    async def download_file(self,content):
        # Specify path 
        filename = content.id + ".mp4"
        path = './' + filename
        # Check whether the specified 
        # path exists or not 
        if(os.path.exists(path)):
            print('file already exists, skippping: ',filename)
        else:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(content.url) as response:
                        if response.status != 200:
                            resp ={"error": f"server returned {response.status}"}
                        else:
                            filename = content.id + ".mp4"
                            print(filename)
                            with open(filename, mode="wb") as file:
                                while True:
                                    chunk = await response.content.read()
                                    if not chunk:
                                        break
                                    file.write(chunk)
                            print(f"Downloaded file {content.name}")
                except asyncio.TimeoutError:
                    print(f"timeout error on {content.url}")

    async def download_content(self,contents):
        start_time = time.time()    
        print(contents)
        n=3
        subarrays = []
        for i in range(0, len(contents), 3):
            subarrays.append(contents[i:i+3])
        for a in subarrays:
            tasks = [self.download_file(url) for url in a]
            await asyncio.gather(*tasks)
        print('download done')
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("\nAll tasks completed in {:.2f} seconds".format(elapsed_time))
        # All tasks completed in 994.13 seconds for TASSO folder

    
"""
#if __name__ == "__main__":
#    asyncio.run(me())
"""