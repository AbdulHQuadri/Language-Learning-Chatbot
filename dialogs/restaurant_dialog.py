from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogSet, DialogTurnResult, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, TurnContext
import random


class RestaurantDialog:
    def __init__(self, conversation_state):
        self.conversation_state = conversation_state
        self.dialog_state = conversation_state.create_property("DialogState")
        self.dialogs = DialogSet(self.dialog_state)

        # Register the prompts and dialogs
        self.dialogs.add(TextPrompt("text_prompt"))
        self.dialogs.add(WaterfallDialog("main_dialog", [self.handle_user_request_step]))

        self.checkpoints = [
            "greet_waiter", "ask_menu", "inquire about a dish", "ask for the special", "order_drink", "order_appetizer", "order_main", "ask_portion_size", "request_customisation", "ask for recommendation", "ask_refill", "request_condiments", "ask_for_cheque", "thank_waiter"
        ]

        self.selected_checkpoints = random.sample(self.checkpoints, 5)
        self.completed_checkpoints = []

    # Single step that continuously handles user requests
    async def handle_user_request_step(self, step_context: WaterfallStepContext):
        user_message = step_context.context.activity.text.lower()
        intent = self.detect_intent(user_message)
        
        if intent == 'greet':
            await step_context.context.send_activity("Hi! Welcome to our restaurant. What can I help you with today?")
        elif intent == 'menu':
            await step_context.context.send_activity("Here's our menu: [Insert menu items here]. What would you like to order?")
        elif intent == 'order':
            selected_item = self.extract_order_item(user_message)
            if selected_item:
                await step_context.context.send_activity(f"Great choice! We'll prepare your {selected_item}.")
            else:
                await step_context.context.send_activity("Sorry, I didn't catch what you'd like to order. Could you please repeat?")
        elif intent == 'cheque':
            await step_context.context.send_activity("Here's your check. Thank you for dining with us!")
            return await step_context.end_dialog()
        else:
            await step_context.context.send_activity("Sorry, I didn't understand that.")
        
        return await step_context.prompt("text_prompt", PromptOptions(prompt=MessageFactory.text("What would you like to do next?")))

#Starts the conversation waterfall.

    async def on_message_activity(self, turn_context: TurnContext):
        dialog_context = await self.dialogs.create_context(turn_context)
        
        # Continue or start the dialog
        if dialog_context.active_dialog:
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")
        
        # Save conversation state
        await self.conversation_state.save_changes(turn_context)

    async def start_dialog(self, turn_context):
        dialog_context = await self.dialogs.create_context(turn_context)
        await dialog_context.begin_dialog("main_dialog")

    def extract_order_item(self, user_message):
        order_phrases = ['i would like to order', 'i want to order', "i'll be having"]

        for phrase in order_phrases:
            if phrase in user_message:
                parts = user_message.split(phrase)
                if len(parts) > 1:
                    # Extract the first two words after the phrase
                    return " ".join(parts[1].strip().split()[:2])  # Adjust the number of words to capture as needed

        return None
    
    #Check the contents of the message to try and match the intent
    def detect_intent(self, user_message):
        if 'hello' in user_message:
            return 'greet'
        elif 'menu' in user_message:
            return 'menu'
        elif any(phrase in user_message for phrase in ['i would like', 'i want to order', "i'll be having"]):
            return 'order'
        elif 'cheque' in user_message or 'bill' in user_message:
            return 'cheque'
        return 'unknown'
    

