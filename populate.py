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
           "can be reached by ascending the stone steps leading up the hill. "
         }

street2 = {"name" : "street2",
           "desc" : "The street continues north and east " \
           "between quaint little cottages with flowerbeds in their " \
           "front yards. " \
           "Across a low stone wall to the west lies a peaceful pond. "
           }

street3 = {"name" : "street3",
           "desc" : "This narrow, twisty street continues south and west " \
           "among buildings of different kinds on each side. " \
           "To the north, behind some other buildings, lies what looks to "
           "be a windmill of some description. "
           }

street4 = {"name" : "street4",
           "desc" : "The street runs north and south. " \
           "On a hill to the west there is a small temple. "
           }

cemetery1 = {"name" : "cemetery1",
             "desc" : "This spooky cemetery seems to be largely abandoned. " \
             "There are cracked tombstones everywhere, covered with moss. " \
             "A temple is visible to the north."
             }

town = [ temple1, cemetery1, street1, street2, street3, street4]

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
    street2   = Room.get(Room.name == "street2")
    street3   = Room.get(Room.name == "street3")
    street4   = Room.get(Room.name == "street4")

    temple1.north   = street1
    temple1.east    = street4
    temple1.south   = cemetery1

    cemetery1.north = temple1

    street1.east    = street3
    street1.south   = temple1
    street1.west    = street2

    street2.east    = street1

    street3.west    = street1
    street3.south   = street4

    street4.north   = street3
    street4.west    = temple1

    for room in [ temple1, cemetery1, street1, street2, street3, street4 ]:
        room.save()

