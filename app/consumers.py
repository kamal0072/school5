#making a chat application with static group name
import json
from channels.consumer import SyncConsumer,AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from .models import Group,Chat
from channels.db import database_sync_to_async

class MySyncConsumer(SyncConsumer):
    def websocket_connect(self,event):
        print("Web socket connected!!!",event)
        print("Channels layers-----------",self.channel_layer) #get default channel layer
        print("Channels Name-----------",self.channel_name) #channel name
        
        self.group_name=self.scope['url_route']['kwargs']['groupsname']
        print("Group Name:.......",self.group_name)
        #Making group of channels--------
        #adding a channel to a new or existing group
        # async_to_sync(self.channel_layer.group_add)("programmers_group_name",self.channel_name)
        async_to_sync(self.channel_layer.group_add)(self.group_name,self.channel_name)
       
        self.send({
            "type":'websocket.accept'
        })
    
    def websocket_receive(self,event):
        print('Message Received from client!!!',event)
        print('Text Message from client!!!',event['text'])
        print("type of message recieved from client: ",type(event['text']))

        data=json.loads(event['text'])
        print("Data....",data)
        print("Type of data....",type(data))
        print("Chat message.....",data['msg'])

        #code finding the user
        print(self.scope['user'])
        #finding group object
        group=Group.objects.get(name=self.group_name)
        if self.scope['user'].is_authenticated:
        #creating chat objects
            chat=Chat(
                content=data['msg'],
                group=group
            )
            chat.save()
            data['user']=self.scope['user'].username
            print("Complete Data: ",data)
            print(" Type of complete Data: ",type(data))
            #sending message to client----------
            async_to_sync(self.channel_layer.group_send)(self.group_name,{
                    'type':'chat.message',
                    'message':json.dumps(data),
                })
        else:
            self.send({
                'type':'websocket.send',
                "text":json.dumps({'msg':'Login required!!'})
            })
    def chat_message(self,event):
        print("Send event---------",event)
        print("Actual message from client---------",event['message'])
        print("Type of Actual message from client---------",type(event['message']))
        self.send({
            "type":'websocket.send',
            'text':event['message']
        })

    def websocket_disconnect(self,event):
        print('WebSocket disconnected!!!',event)
        print("Channels layers-----------",self.channel_layer) #get default channel layer
        print("Channels Name-----------",self.channel_name) #channel name
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,self.channel_name
            )
        raise StopConsumer()

#code for AsyncConsumer
class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        print("Web socket connected!!!",event)
        print("Channels layers-----------",self.channel_layer) #get default channel layer
        print("Channels Name-----------",self.channel_name) #channel name

        #Making group of channels--------
        #adding a channel to a new or existing group
        await self.channel_layer.group_add(self.group_name,self.channel_name)
       
        await self.send({
                "type":'websocket.accept'
            })
    
    async def websocket_receive(self,event):
        print('Message Received from client!!!',event)
        print('Text Message from client!!!',event['text'])
        print("type of message recieved from client: ",type(event['text']))
        data=json.loads(event['text'])
        print("Data....",data)
        print("Type of data....",type(data))
        print("Chat message.....",data['msg'])

        #finding group object
        group=await database_sync_to_async(Group.objects.get)(name=self.group_name)
        if self.scope['user'].is_authenticated:
            #creating chat objects
            chat=Chat(
                content=data['msg'],
                group=group
            )
            await database_sync_to_async(chat.save)()
            #sending message to client----------
            await self.channel_layer.group_send('programmers_group_name',{
                    'type':'chat.message',
                    'message':event['text'],
                })
        else:
            await self.send({
                'type':'websocket.send',
                "text":json.dumps({'msg':'Login required!!'})
            })
    async def chat_message(self,event):
        print("Send event---------",event)
        print("Actual message from client---------",event['message'])
        print("Type of Actual message from client---------",type(event['message']))
        await self.send({
            "type":'websocket.send',
            'text':event['message']
        })

    async def websocket_disconnect(self,event):
        print('WebSocket disconnected!!!',event)
        print("Channels layers-----------",self.channel_layer) #get default channel layer
        print("Channels Name-----------",self.channel_name) #channel name
        await self.channel_layer.group_discard(
            "programmers_group_name",self.channel_name
            )
        raise StopConsumer()
