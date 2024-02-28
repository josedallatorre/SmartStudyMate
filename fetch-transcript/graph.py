# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# <UserAuthConfigSnippet>
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.teams.teams_request_builder import TeamsRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder)
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody)
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress

class Graph:
    settings: SectionProxy
    client_credential: DeviceCodeCredential
    app_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')
        client_secret = self.settings['clientSecret']

        self.client_credential = DeviceCodeCredential(client_id=client_id, tenant_id= tenant_id)
        self.app_client = GraphServiceClient(self.client_credential, scopes=graph_scopes) # type: ignore
# </UserAuthConfigSnippet>

    # <GetUserTokenSnippet>
    async def get_app_only_token(self):
        access_token = await self.client_credential.get_token(self.graph_scopes)
        return access_token.token
    # </GetUserTokenSnippet>

    # <GetUserSnippet>
    async def get_user(self):
        # Only request specific properties using $select
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user = await self.app_client.me.get(request_configuration=request_config)
        return user
    # </GetUserSnippet>

    # <GetInboxSnippet>
    async def get_inbox(self):
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['from', 'isRead', 'receivedDateTime', 'subject'],
            # Get at most 25 results
            top=25,
            # Sort by received time, newest first
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters= query_params
        )

        messages = await self.app_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config)
        return messages
    # </GetInboxSnippet>

    # <SendMailSnippet>
    async def send_mail(self, subject: str, body: str, recipient: str):
        message = Message()
        message.subject = subject

        message.body = ItemBody()
        message.body.content_type = BodyType.Text
        message.body.content = body

        to_recipient = Recipient()
        to_recipient.email_address = EmailAddress()
        to_recipient.email_address.address = recipient
        message.to_recipients = []
        message.to_recipients.append(to_recipient)

        request_body = SendMailPostRequestBody()
        request_body.message = message

        await self.app_client.me.send_mail.post(body=request_body)
    # </SendMailSnippet>

    # <MakeGraphCallSnippet>
    async def make_graph_call(self):
        # INSERT YOUR CODE HERE
        me = await self.app_client.me.get()
        if me:
            print(me.display_name)

        """
        
        query_params = TeamsRequestBuilder.TeamsRequestBuilderGetQueryParameters(
            select = ['id','description','displayName']
        )

        request_config = TeamsRequestBuilder.TeamsRequestBuilderGetRequestConfiguration(
            query_parameters = query_params,
        )
        """

        result = await self.app_client.me.joined_teams.get()
        print(result)
        """
        choice = input("id?")
        result2 = await self.app_client.groups.by_group_id(choice).events.get()
        print(result2)
        """
        result3 = await self.app_client.communications.online_meetings.get()
        print(result3)
        # THE PYTHON SDK IS IN PREVIEW. FOR NON-PRODUCTION USE ONLY

        result4 = await self.app_client.users.by_user_id('4c675eae-8304-4358-b9f7-d4480cfc798b').online_meetings.by_online_meeting_id('AAMkAGFjNmZhMDRiLTU1OGEtNGM3OC05MGFlLTllODk0OWYzNjFmYQBGAAAAAAD3p0rX5oaDSp0zUxLz21soBwBHgbmfciJ1Q6vNMjBkuvckAAAAAAENAABHgbmfciJ1Q6vNMjBkuvckAABrzcrQAAA=').transcripts.get()
        print(result4)

        #get children of coppola folder
        #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVV7DNQJHIKYC4BFLBZOKORXABDCM/children/

        #get a content
        #https://graph.microsoft.com/v1.0/groups/1fd60a75-9f61-437c-b4c5-5b400cbf9d4f/drive/items/01GQ6WVVZS27LN2OKLGVBLQXK5ESUXJGK4/content

        return 
    # </MakeGraphCallSnippet>
