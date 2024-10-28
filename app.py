from flask import Flask, request
from botbuilder.core import TurnContext, ActivityHandler,ConversationState, MemoryStorage,MessageFactory, BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.dialogs import DialogSet, WaterfallDialog, WaterfallStepContext, TextPrompt
from botbuilder.dialogs.prompts import PromptOptions
from botbuilder.schema import Activity
from botbuilder.core.state_property_accessor import StatePropertyAccessor
from dialogs.restaurant_dialog import RestaurantDialog
# from dialogs.travel_dialog import TravelDialog
from utils.message_handler import MessageHandler
import asyncio

#Bots are event driven os come in as activities. Bot response is based on incoming activity. Event driven programming, bot reacts to user inputs
#Bot is created by subclassing ActivityHandler from bot builder core.


app = Flask(__name__)

# Adapter settings (App ID and password are not needed for local development)
adapter_settings = BotFrameworkAdapterSettings("","")
adapter = BotFrameworkAdapter(adapter_settings)

#Memory Settings for conversation storage
memory = MemoryStorage()
conversation_state = ConversationState(memory)

class MyBot(ActivityHandler): 
    def __init__(self, conversation_state):
        self.conversation_state = conversation_state
        self.dialog_state = conversation_state.create_property("DialogState")
        self.message_handler = MessageHandler(conversation_state)
    
    async def on_message_activity(self , turn_context: TurnContext):
        #Give the messages to the message handler
        await self.message_handler.handle_message(turn_context)


# This route handles POST requests to the bot
@app.route("/api/messages", methods=["POST"])

def messages():
    body = request.json
    activity = Activity.deserialize(body)

    async def turn_call(turn_context: TurnContext):
        await bot.on_turn(turn_context)
    
    task = asyncio.run(adapter.process_activity(activity, None, turn_call))
    
    # Return an HTTP 200 response
    return "OK", 200


if __name__ == "__main__":
    bot = MyBot(conversation_state)
    app.run(port=3978, debug=True)