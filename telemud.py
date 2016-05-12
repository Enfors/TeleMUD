#!/usr/bin/env python3

import sys, time, telepot

from peewee import *

import keyboard

database = SqliteDatabase("database.db")

online_users = { }

class TeleMUDBot(telepot.Bot):

    def __init__(self, *args, **kwargs):
        super(TeleMUDBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self) # Unneeded?

        self.loaded_rooms = { }
        
        self.command_funcs = {
            "look"    : self.do_look,
            "go"      : self.do_go,
            "say"     : self.do_say,
            "attack"  : self.do_attack,
            "objects" : self.do_objects,
            "help"    : self.do_help,
        }


    def handle(self, msg):

        """Handle incoming Telegram messages."""

        flavor = telepot.flavor(msg) # Messages come in different flavors.
                                     # We are only interested in private
                                     # chat messages.

        if flavor != "chat":
            print("Unsupported message flavor ignored: %s" % flavor)

        content_type, chat_type, chat_id = telepot.glance(msg)

        # The message contains information about who sent it, as well
        # as the actual text.
        user_name = msg["from"]["first_name"]
        text      = msg["text"]

        print("<- %-10s: %s" % (user_name, text))

        # The output variable will be sent as a response to the user
        # at the end of this function.
        output = ""

        # First, check if the user is logged in, or if this is their
        # first message.
        if user_name not in online_users: # If login
            (login_output, user) = self.user_login(user_name, chat_id)
            output += login_output
            # Since the user is just logging in, we don't need to
            # look at what they entered in the message. It was
            # probably just '/start' or somesuch. We just want to
            # send them the login greeting.

            # Since the user just logged on, we should turn on the
            # default keyboard.
        else:                             # If already logged in user
            # This is an already logged in user. Find the user object.
            user = self.find_online_user(user_name)

            # Check if we're waiting for something special from the user
            input_func = user.get_input_func()
            if input_func:
                output = input_func(user, text)
                
            else:
                # Execute the command entered by the user.
                output = self.parse_and_execute_command(user, text)

        # If there was output generated by whatever the user did,
        # we want to send it back to the user.
        if output:
            display = output.replace("\n", "\\n")
            if len(display) > 60:
                display = display[:59] + "[...]"
            print("-> %-10s: %s" % (user_name, display))

            # This is the line that sends the output to the user.
            bot.sendMessage(chat_id, output)

        if user.show_keyboard:
            user.get_keyboard().show(user)
            user.show_keyboard = False


    def parse_and_execute_command(self, user, text):
        # Separate the user input into words.
        words   = text.split(" ")
        command = words[0].lower() # The first word is the command.
        
        if len(words) > 1: # If there are more words, the rest are args.
            args = words[1:]
        else:
            args = None

        # Check if the command is valid.
        if not self.is_valid_command(user, command, args):
            output = "I'm sorry, I don't understand."
        else:
            # The command is valid, so let's execute it.
            output = self.command_funcs[command](user, command, args)

        # Send the output back to the calling function, so that it
        # can send it to the user.
        return output

            
    def user_login(self, user_name, chat_id):

        output = ""
        
        login_room = self.find_room_by_id(1)

        new_user = User()
        new_user.input_func = None
        
        output += new_user.login(self, user_name, chat_id)

        login_room.receive_obj(new_user)

        output += self.do_look(new_user)

        online_users[user_name] = new_user

        return output, new_user


    def is_valid_command(self, user, command, args):
        if command in self.command_funcs:
            return True
        else:
            return False
    
    
    # Command functions
    def do_look(self, doer, command = "look", args = []):

        output = ""

        room = doer.room
        
        if not room:
            return "You seem to be... nowhere. How strange."
            
        desc = room.get_desc()

        if len is None or len(desc) < 1:
            desc = "This is an exceedingly non-descript room. "
            
        output += desc + "\nExits: " + room.get_exits_desc() + "\n"

        content = room.get_content()

        for obj in content:
            #print("- Considering '%s'..." % obj)
            if obj is not doer: # We don't need to see ourselves.
                output += "%s is here.\n" % obj

        return output


    def do_go(self, doer, command = "go", args = []):

        output = ""

        if len(args) < 1: # If there are no args:
            return "Go in which direction?"

        starting_room = self.environment(doer)

        if not starting_room:
            login_room.receive_obj(doer)
            return "How strange. You don't seem to be anywhere. " \
                "Not to worry though, I've put you in the login room. "

        direction = args[0].lower()

        new_room = self.find_connecting_room(starting_room, direction)

        if new_room:
            starting_room.remove_obj(doer)
            starting_room.receive_text("%s goes %s." %
                                       (doer.get_name(), direction))
            new_room.receive_text("%s arrives." % doer.get_name())
            new_room.receive_obj(doer)
            output += self.do_look(doer)
        else:
            output += "You can't go what way."

        return output


    def do_say(self, doer, command = "say", args = []):

        room = self.environment(doer)

        if not room:
            return False

        if not args:
            doer.set_input_func(self.do_pending_say)
            doer.keyboard.hide(doer)
            return "What do you want to say?"

        say_string = "%s says: %s" % (doer.get_name(), " ".join(args))

        room.receive_text(say_string)

        return ""


    def do_pending_say(self, doer, text):
        doer.clear_input_func()
        doer.show_keyboard = True
        self.parse_and_execute_command(doer, "say " + text)
        return None
        

    def do_attack(self, doer, command = "attack", args = []):
        return "[Attack: not implemented]"


    def do_objects(self, doer, command = "objects", args = []):
        return "[Objects: not implemented]"


    def do_help(self, doer, command = "help", args = []):
        return "[Help: not implemented]"

        
    # Utility functions
    def environment(self, obj):
        if not obj:
            print("environment(): Warning: called on null obj.")
            return None
        else:
            return obj.room
    
    
#    def find_room_by_name(self, name):
#        return Room.get(Room.name == name)


    def find_room_by_id(self, room_id):

        #print("=== Looking for room %d..." % room_id)
        #print("= loaded_rooms: ")
        #print(self.loaded_rooms)
        
        if room_id in self.loaded_rooms:
            #print("= It is loaded already.")
            return self.loaded_rooms[room_id]
        else:
            #print("= I had to load it.")
            self.loaded_rooms[room_id] = Room.get(Room.id == room_id)

        return self.loaded_rooms[room_id]
    

    def find_connecting_room(self, starting_room, direction):
        if not starting_room:
            print("find_connecting_room(): Warning: "
                  "called on null starting_room.")
            return None

        if not direction or len(direction) < 1:
            print("find_connecting_room(): Warning: " \
                  "called on empty direction.")
            return None

        if direction == "north":
            dest_room = self.find_room_by_id(starting_room.north_id)
        elif direction == "east":
            dest_room = self.find_room_by_id(starting_room.east_id)
        elif direction == "south":
            dest_room = self.find_room_by_id(starting_room.south_id)
        elif direction == "west":
            dest_room = self.find_room_by_id(starting_room.west_id)
        else:
            print("find_connecting_room(): Warning: "
                  "invalid direction '%s'" % direction)
            return None

        return dest_room
    

    def find_user_in_database(self, name):
        return User.get(User.name == name)


    def find_online_user(self, name):
        try:
            return online_users[name]
        except KeyError:
            return None



class Obj(Model):

    def receive_text(self, text):
        pass


#    def __str__(self):
#        try:
#            return self.desc
#        except AttributeError:
#            return "An object of which the author forgot to " \
#                "provide a description. "



class Container(Obj):

    def add_content(self, obj):
        # todo: This is an ugly hack, because I don't know enough
        # to make it work with an __init__ for this class. Adding
        # one messes up populate.py.
        try:
            if not self.content:
                self.content = [ ]
        except AttributeError:
            self.content = [ ]
            
        self.content.append(obj)

        #print("Container: Adding %s to %s." % (obj, self))
        
        obj.room = self


    def remove_content(self, obj):
        if not self.content:
            self.content = [ ]

        if obj not in self.content:
            return False    
        
        self.content.remove(obj)


    def get_content(self):
        return self.content
        

    # Objects shouldn't overload this function. Overload on_text()
    # instead.
    def receive_text(self, text, exclude = [ ]):

        self.on_text(text)

        # Hack alert (todo: fix this when I know how)
        # This is a problem right now since I can't add an
        # __init__ to the User class.
        try:
            for obj in self.content:
                if obj not in exclude:
                    obj.receive_text(text)
        except AttributeError:
            pass


    def on_text(self, text):
        pass
        
    

class Room(Container):
    name = CharField(unique = True)
    desc = CharField()

    north = ForeignKeyField('self', null = True, related_name="north_exit")
    east  = ForeignKeyField('self', null = True, related_name="east_exit")
    south = ForeignKeyField('self', null = True, related_name="south_exit")
    west  = ForeignKeyField('self', null = True, related_name="west_exit")

    def get_desc(self):
        return self.desc


    def get_exits_desc(self):
        output = ""
        if self.north:
            output += "North "
        if self.east:
            output += "East "
        if self.south:
            output += "South "
        if self.west:
            output += "West "

        return output


    def receive_obj(self, obj):
        self.add_content(obj)

        #print("%s entered me (%s)." % (obj, self));
    

    def remove_obj(self, obj):
        self.remove_content(obj)

        #print("%s left me." % obj)

        
    class Meta:
        database = database


        
class User(Container):
    name    = CharField(unique = True)
    chat_id = IntegerField(unique = True)
    room    = ForeignKeyField(Room, null = True)

    def login(self, bot, name, chat_id):

        output = ""
        
        try: # If user already exists in the database:
            self.get(User.name == name)
        except:
            output += "Ah, your first visit I see. "
            self.name    = name
            self.chat_id = chat_id
            self.save()

        self.name    = name
        self.chat_id = chat_id
        self.bot = bot
        self.set_keyboard(keyboard.Keyboard(bot))
        self.show_keyboard = True
            
        output += "Welcome to TeleMUD!\n\n"

        return output

    def get_name(self):
        return self.name
    

    def get_chat_id(self):
        return self.chat_id


    def set_keyboard(self, new_keyboard):
        self.keyboard = new_keyboard
        return None


    def get_keyboard(self):
        return self.keyboard


    def set_input_func(self, input_func):
        self.input_func = input_func

    
    def get_input_func(self):
        return self.input_func


    def clear_input_func(self):
        self.input_func = None
        return None
    
    
    def on_text(self, text):
        self.bot.sendMessage(self.chat_id, text)

    
    def __str__(self):
        return self.name + " (player)"
    

    class Meta:
        database = database



if __name__ == "__main__":

    with open("token", "r") as token_file:
        token = token_file.read().replace("\n", "")
    
    bot = TeleMUDBot(token)

    bot.message_loop()
    print("Started.")

    while True:
        time.sleep(10)
    