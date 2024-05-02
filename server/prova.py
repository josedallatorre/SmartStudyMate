from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient
import asyncio 

async def me():
    credential = InteractiveBrowserCredential()
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credential, scopes)
    me = await graph_client.me.get()
    teams = await graph_client.me.joined_teams.get()
    print(teams)
    group_id = input("group id?")
    drive = await graph_client.groups.by_group_id(group_id).drive.get()
    print(drive)
    drive_id = input("drive id?")
    root = await graph_client.drives.by_drive_id(drive_id).root.get()
    print(root)
    childrens = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id('01GQ6WVV56Y2GOVW7725BZO354PWSELRRZ').children.get()
    print(childrens)

    #get root folder of the group and list children
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/root/children
    
    #get children of "COPPOLA" folder
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVV7DNQJHIKYC4BFLBZOKORXABDCM/children/

    #get a content
    #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVVZS27LN2OKLGVBLQXK5ESUXJGK4/content


if __name__ == "__main__":
    asyncio.run(me())