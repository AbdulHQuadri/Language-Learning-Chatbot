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

        # self.checkpoints = [
        #     "greet_waiter", "ask_menu", "inquire about a dish", "ask for the special", "order_drink", "order_appetizer", "order_main", "ask_portion_size", "request_customisation", "ask for recommendation", "ask_refill", "request_condiments", "ask_for_cheque", "thank_waiter"
        # ]

        # self.selected_checkpoints = random.sample(self.checkpoints, 5)
        # self.completed_checkpoints = []

    # Single step that continuously handles user requests
    async def handle_user_request_step(self, step_context: WaterfallStepContext):
        user_message = step_context.context.activity.text.lower()
        intent = self.detect_intent(user_message)
        
        # Handle greeting
        if intent == 'greet':
            await step_context.context.send_activity("Hi! Welcome to our restaurant. How can I assist you today?")
        
        # Handle menu request
        elif intent == 'menu':
            await step_context.context.send_activity("Here's our menu: [Insert menu items here]. Let me know if you have any questions or if something catches your eye!")

        # Handle order request
        elif intent == 'order':
            selected_item = self.extract_order_item(user_message)
            if selected_item:
                await step_context.context.send_activity(f"Great choice! We'll start preparing your {selected_item} right away. Anything else you’d like?")
            else:
                await step_context.context.send_activity("I didn’t quite catch that. Could you let me know what you’d like to order again?")

        # Handle dish alterations
        elif intent == 'altered_dish':
            await step_context.context.send_activity("Of course! I'll inform the chef about your preference to [add alteration here]. Anything else I can adjust for you?")

        # Handle dietary information requests
        elif intent == 'dietary_info':
            await step_context.context.send_activity("[Check the dietary information inside the database]. Yes, the [meal] is [dietary-requirement]. Or, I can suggest [another meal that matches]. Let me know your preference!")

        # Handle drink orders
        elif intent == 'order_drink':
            await step_context.context.send_activity("Certainly! Would you like sparkling water, soda, or perhaps something else?")

        # Handle compliments
        elif intent == 'compliment':
            await step_context.context.send_activity("Thank you so much! I’ll let the chef know you enjoyed it. Is there anything else I can bring for you?")

        # Handle check request
        elif intent == 'cheque':
            await step_context.context.send_activity("Of course. I’ll get your check right away. Thank you for dining with us! Hope to see you again soon!")
            return await step_context.end_dialog()  # End dialog as it’s a closing interaction
        
        elif intent == 'closing':
            await step_context.context.send_activity("Thank you for dining with us today")
            return await step_context.end_dialog()  # End dialog as it’s a closing interaction

        # Handle unknown intent
        else:
            await step_context.context.send_activity("Sorry, I didn't understand that. I'm here to help with anything restaurant-related. Could you please rephrase your request?")

        # Keep dialog open for follow-up
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
    
    async def end_dialog(self, step_context:WaterfallStepContext):
        await step_context.context.send_activity("This would be the end of a certain level or setting task")

        return await step_context.end_dialog()


    def extract_order_item(self, user_message):
        order_phrases = ['i would like', 'i want to order', "i'll be having", 'i’ll have', 'get', 'like to order']

        for phrase in order_phrases:
            if phrase in user_message:
                parts = user_message.split(phrase, 1)
                if len(parts) > 1:
                    # Capture two or three words following the order phrase for more flexibility
                    return " ".join(parts[1].strip().split()[:3])

        return None
    
    #Check the contents of the message to try and match the intent
    def detect_intent(self, user_message):
        user_message = user_message.lower()

        # Greeting
        if 'hello' in user_message or 'hi' in user_message:
            return 'greet'

        # Requesting a menu
        elif any(phrase in user_message for phrase in ['menu', 'see menu', 'food options', "what's on the menu"]):
            return 'menu'

        # Ordering
        elif any(phrase in user_message for phrase in ['i would like', 'i want to order', "i'll be having", 'i’ll have', 'get', 'like to order']):
            return 'order'

        # Request an altered dish
        elif any(phrase in user_message for phrase in ['add', 'without', 'no', 'extra', 'change', 'modify']):
            return 'altered_dish'

        # Asking for dietary information intent
        elif any(phrase in user_message for phrase in ['gluten-free', 'dietary', 'allergy', 'allergic', 'ingredients', 'contain']):
            return 'dietary_info'

        # Requesting a drink intent
        elif any(phrase in user_message for phrase in ['drink', 'water', 'sparkling', 'still', 'soda', 'wine', 'beverage']):
            return 'order_drink'

        # Giving a compliment intent
        elif any(phrase in user_message for phrase in ['delicious', 'good', 'great', 'tasty', 'compliment', 'chef']):
            return 'compliment'

        # Asking for the cheque
        elif 'cheque' in user_message or 'bill' in user_message:
            return 'cheque'

        # Closing phrases
        elif any(phrase in user_message for phrase in ['thank you', 'thanks', 'goodbye', 'bye', 'see you', 'exit']):
            return 'closing'

        # Unknown or unspecified intent
        return 'unknown'
