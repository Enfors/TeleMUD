#!/usr/bin/env python3

import datetime
import peewee

from telemud import Room, User

# This is a TERRIBLE way of making areas. This will change in the future.
# This code sucks. The idea is that you'll be able to create areas from
# inside the game eventually.

temple1 = {"name" : "temple1",
           "desc" : "This is a small square-shaped temple " \
           "with marble pillars along the relief-covered walls. " \
           "The view through the open exits in all directions reveal that " \
           "the temple seems to be located on a hill in the center of a " \
           "picturesque little town. "
         }
street1 = {"name" : "street1",
           "desc" : "A narrow street running east and west, " \
           "just north of the temple. " \
           "Buildings block movement to the north, but the temple " \
           "can be reached by by ascending the stone steps leading up the hill. "
         }

cemetery1 = {"name" : "cemetery1",
             "desc" : "This spooky cemetery seems to be largely abandoned. " \
             "There are cracked tombstones everywhere, covered with moss. " \
             "A temple is visible to the north."
             }

town = [ temple1, cemetery1, street1 ]

if __name__ == "__main__":
    try:
        Room.create_table()
    except peewee.OperationalError:
        print("Room table already exists.")
        
    try:
        User.create_table()
    except peewee.OperationalError:
        print("User table already exists.")

    for room in town:
        r = Room(**room)
        r.save()

    temple1   = Room.get(Room.name == "temple1")
    cemetery1 = Room.get(Room.name == "cemetery1")
    street1   = Room.get(Room.name == "street1")

    temple1.north = street1
    temple1.south = cemetery1

    cemetery1.north = temple1
    
    street1.south = temple1

    for room in [ temple1, cemetery1, street1 ]:
        room.save()

