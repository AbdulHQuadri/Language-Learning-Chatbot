from dialogs.restaurant_dialog import RestaurantDialog
# from dialogs.travel_dialog import TravelDialog
# from dialogs.interaction_dialog import InteractionDialog

class MessageHandler:
    def __init__(self, conversation_state):
        self.restaurant_dialog = RestaurantDialog(conversation_state,'GMIYP7KCK7C2RVHWSDSABYBKKO4M52N2')
        # self.travel_dialog = TravelDialog(conversation_state)
        # self.interaction_dialog = InteractionDialog(conversation_state)

    async def handle_message(self, turn_context):
        user_message = turn_context.activity.text.lower()

        if "menu" or "hungry" or "food" or "restaurant" in user_message:
            await self.restaurant_dialog.start_dialog(turn_context)
        # elif 'travel' in user_message or 'city' in user_message:
        #     await self.travel_dialog.start_dialog(turn_context)
        # else:
        #     await self.interaction_dialog.start_dialog(turn_context)