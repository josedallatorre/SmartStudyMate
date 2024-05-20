import asyncio
import configparser
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from graph import Graph
from dotenv import load_dotenv
import os

async def main():
    print('SmartStudyMate\n')
    load_dotenv()
    # Load settings
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    CLIENT_ID = os.getenv("CLIENT_ID")
    if not CLIENT_SECRET:
        raise ValueError("Need to define CLIENT_SECRET environment variable")
    if not CLIENT_ID:
        raise ValueError("Need to define CLIENT_ID environment variable")


    graph: Graph = Graph()

    await greet_user(graph)

    choice = -1

    while choice != 0:
        print('Please choose one of the following options:')
        print('0. Exit')
        print('1. Display access token')
        print('2. get joined teams')
        print('3. get drive root')
        print('4. get drive childerns')
        print('5. get children id')
        print('6. get drive')

        try:
            choice = int(input())
        except ValueError:
            choice = -1

        try:
            if choice == 0:
                print('Goodbye...')
            elif choice == 1:
                await display_access_token(graph)
            elif choice == 2:
                await get_joined_teams(graph)
            elif choice == 3:
                await get_drive_root(graph)
            elif choice == 4:
                await get_drive_childrens(graph)
            elif choice == 5:
                await get_children_id(graph)
            elif choice == 6:
                await get_drive(graph)
            else:
                print('Invalid choice!\n')
        except ODataError as odata_error:
            print('Error:')
            if odata_error.error:
                print(odata_error.error.code, odata_error.error.message)
# </ProgramSnippet>

# <GreetUserSnippet>
async def greet_user(graph: Graph):
    user = await graph.me()
    if user:
        print('Hello,', user.display_name)
        # For Work/school accounts, email is in mail property
        # Personal accounts, email is in userPrincipalName
        print('Email:', user.mail or user.user_principal_name, '\n')
# </GreetUserSnippet>

# <DisplayAccessTokenSnippet>
async def display_access_token(graph: Graph):
    token = await graph.get_app_only_token()
    print('User token:', token, '\n')
# </DisplayAccessTokenSnippet>

async def get_joined_teams(graph: Graph):
    teams = await graph.get_joined_teams()
    print('User joined teams:', teams, '\n')

async def get_drive(graph:Graph):
    group_id = input('group id?\n')
    drive = await graph.get_drive(group_id)
    print('Drive:', drive,'\n')

async def get_drive_root(graph:Graph):
    drive_id = input('drive id?\n')
    root = await graph.get_drive_root(drive_id)
    print('Drive: root', root,'\n')

async def get_drive_childrens(graph:Graph):
    drive_id = input('drive id?\n')
    drive_item = input('drive item?\n')
    drive_childrens = await graph.get_drive_childrens(drive_id,drive_item)
    print('Drive childrens: ', drive_childrens,'\n')

async def get_children_id(graph:Graph):
    drive_id = input('drive id?\n')
    childrens_id = input('childrens id?\n')
    children_id = await graph.get_children_id(drive_id,childrens_id)
    print('Drive childrens: ', children_id,'\n')



# Run main
asyncio.run(main())
