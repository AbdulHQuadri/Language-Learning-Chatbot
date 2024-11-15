from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogSet, DialogTurnResult, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, TurnContext
import random, requests, json, sys, os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
# from db_connect import database


class RestaurantDialog:
    def __init__(self, conversation_state, wit_token):
        self.conversation_state = conversation_state
        self.dialog_state = conversation_state.create_property("DialogState")
        self.dialogs = DialogSet(self.dialog_state)
        self.wit_token = wit_token

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
        intent, data = self.detect_intent(user_message)

        # Define response pools
        greetings = [
            "Hi there! Welcome to our restaurant. How can I assist you today?",
            "Hello! Great to have you here. What can I do for you?",
            "Hey! I'm here to help you with anything. What would you like to start with?"
        ]

        menus = [
            "Here's our menu: [Insert menu items]. Let me know if you have any questions!",
            "Our menu has a variety of options for you. Take a look: [Insert menu items here].",
            "Here’s what we have today: [Menu items]. What catches your eye?"
        ]

        compliments = [
            "Thank you so much! I’ll let the chef know you enjoyed it.",
            "We appreciate the kind words! Our chef will be thrilled to hear that.",
            "You just made our day! I'll pass your compliment to the kitchen."
        ]

        cheque_responses = [
            "Sure, I’ll get your check right away. Thanks for dining with us!",
            "Of course, I'll bring the check to you shortly. It was a pleasure serving you!",
            "I’ll prepare your bill right now. We hope to see you again soon!"
        ]

        follow_up_prompts = [
            "Can I help you with anything else?",
            "Is there anything else you’d like to order?",
            "Would you like to see the dessert menu?"
        ]
        
        # Handle greeting
        if intent == 'greet':
            await step_context.context.send_activity(random.choice(greetings))
        
        # Handle menu request
        elif intent == 'get_menu':
            await step_context.context.send_activity(random.choice(menus))

        # Handle order request
        elif intent == 'order':
            entities = data.get('entities', {})

            #Variables to store entity data
            drink_option = [item["value"] for item in entities.get("drink_option:drink_option", [])]
            menu_items = [item["value"] for item in entities.get("food_option:food_option", [])]
            quantities = [int(item["value"]) for item in entities.get("quantity:quantity", [])]

            response_message = ""

            if menu_items:
                for i, menu_item in enumerate(menu_items):
                    quantity = quantities[i] if i < len(quantities) else 1
                    response_message += f"{quantity} x {menu_item}\n"
                
                await step_context.context.send_activity(
                    f"Great choice! We'll start preparing:\n{response_message.strip()}"
                )

                # Offer a drink if no drink_option is found
                if not drink_option:
                    await step_context.context.send_activity("Would you like to add a drink with that order?")
                else:
                    drinks_order = ", ".join(drink_option)
                    await step_context.context.send_activity(
                        f"Got it! You also ordered {drinks_order}. Anything else you'd like?"
                    )
            else:
                await step_context.context.send_activity(
                    "I didn't quite catch that. Could you let me know what you'd like to order again?"
                )


        # Handle dish alterations
        elif intent == 'altered_dish':
            await step_context.context.send_activity("Of course! I'll inform the chef about your preference to [add alteration here]. Anything else I can adjust for you?")

        # Handle dietary information requests
        # elif intent == 'dietary_info':
        #     entities = data.get('entities', {})

        #      # Extract food_option and dietary_info entities
        #     food_option = [item["value"] for item in entities.get("food_option:food_option", [])]
        #     dietary_info = [item["value"] for item in entities.get("dietary_info:dietary_info", [])]

        #     if food_option and dietary_info:
        #     # Query check food requirements for compatible or alternatives
        #         is_compatible, alternatives = await self.check_dietary_info(food_option[0], dietary_info[0])

        #         if is_compatible:
        #             # If the dish matches the dietary information, respond positively
        #             await step_context.context.send_activity(
        #                 f"The {food_option[0]} is suitable for your {dietary_info[0]} preference. Enjoy your meal!"
        #             )
        #         else:
        #             # If not compatible, suggest alternatives
        #             if alternatives:
        #                 alternatives_msg = "\n".join([f"- {alt}" for alt in alternatives])
        #                 await step_context.context.send_activity(
        #                     f"Unfortunately, {food_option[0]} doesn't meet your {dietary_info[0]} preference. However, here are some alternatives:\n{alternatives_msg}"
        #                 )
        #             else:
        #                 await step_context.context.send_activity(
        #                     f"Unfortunately, we don't have any alternatives that fit your {dietary_info[0]} preference at the moment."
        #                 )
        #     else:
        #         await step_context.context.send_activity(
        #             "Please specify both the food and dietary preference so I can help you further."
        #         )


        # Handle drink orders
        elif intent == 'order_drink':
            await step_context.context.send_activity("Certainly! I will get [drink]")

        # Handle compliments
        elif intent == 'compliment':
            await step_context.context.send_activity(random.choice(compliments))

        # Handle check request
        elif intent == 'cheque':
            await step_context.context.send_activity(random.choice(cheque_responses))
            return await step_context.end_dialog()  # End dialog as it’s a closing interaction
        
        elif intent == 'closing':
            await step_context.context.send_activity("Thank you for dining with us today. I'll get your final bill")
            return await step_context.end_dialog()  # End dialog as it’s a closing interaction

        # Handle unknown intent
        else:
            await step_context.context.send_activity("Sorry, I didn't understand that. I'm here to help with anything restaurant-related. Could you please rephrase your request?")

        # Keep dialog open for follow-up
        return await step_context.prompt("text_prompt", PromptOptions(prompt=MessageFactory.text("")))

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

    
    #Check the contents of the message to try and match the intent
    def detect_intent(self, user_message):
            # Send user message to Wit.ai for intent detection
            response = requests.get(
                'https://api.wit.ai/message',
                headers={'Authorization': f'Bearer {self.wit_token}'},
                params={'q': user_message}
            )

            data = response.json()

            print(json.dumps(data, indent=4))
         
             # Extract top intent
            top_intent = data['intents'][0]['name'] if data.get('intents') else 'unknown'
            return top_intent, data

    # def check_dietary_info(self, food_item, dietary_requirement):
    #     connection = database.connect()
    #     cursor = database.get_cursor()
        
    #     food_item = food_item.lower()
    #     dietary_requirement = dietary_requirement.lower()

    #     if connection and cursor:
    #         try:
    #             query = """
    #                 SELECT item_name, additional_info
    #                 FROM menu
    #                 WHERE item_name LIKE %s AND JSON_UNQUOTE(JSON_EXTRACT(additional_info, '$.dietary')) LIKE %s
    #             """
    #             cursor.execute(query, ('%' + food_item + '%', '%' + dietary_requirement + '%'))
    #             results = cursor.fetchall()

    #             # Check compatibility and return alternatives
    #             compatible_items = []
    #             alternatives = []
    #             for result in results:
    #                 item_name = result['item_name']
    #                 additional_info = result['additional_info']
                    
    #                 # Assuming dietary_info field contains a list of dietary preferences
    #                 dietary_info = json.loads(additional_info).get('dietary', [])
    #                 if dietary_requirement in dietary_info:
    #                     compatible_items.append(item_name)
    #                 else:
    #                     alternatives.append(item_name)
                
    #             return compatible_items, alternatives

    #         except Exception as e:
    #             print(f"Error fetching dietary info: {e}")
    #             return [], []
    #         finally:
    #             cursor.close()
        

        



