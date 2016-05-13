class Keyboard:

    def __init__(self, bot):

        self.bot = bot

        self.text    = "What do you want to do?"
        self.buttons = [[ "Say",     "Go north",  "Attack"  ],
                        [ "Go west", "Look",      "Go east" ],
                        [ "Status",  "Go south",  "Help"    ]]
        return None

    
    def show(self, user):
        self.bot.sendMessage(user.get_chat_id(),
                             self.text,
                             reply_markup = { "keyboard" : self.buttons})
        return None


    def hide(self, user):
        self.bot.sendMessage(user.get_chat_id(),
                             "Hiding the keyboard.",
                             reply_markup = { "hide_keyboard": True })
        return None
    


class BigKeyboard(Keyboard):

    def __init__(self, bot):
        super().__init__(bot)

        self.buttons = [["Say",    "North",   "Shout",   "Attack"  ],
                        ["West",   "Look",    "East",    "Objects" ],
                        ["Status", "South",   "Hide",    "Search", ],
                        ["Prev",   "Who",     "Help",    "Next"    ]]
        
