#!/usr/bin/env python3

import peewee

database = peewee.SqliteDatabase("testdb.db")

class Room(peewee.Model):

    name  = peewee.CharField()
    north = peewee.ForeignKeyField('self', null = True, related_name="north_exit")
    south = peewee.ForeignKeyField('self', null = True, related_name="south_exit")

    class Meta:
        database = database


if __name__ == "__main__":
    print("Running...")
    try:
        Room.create_table()
    except peewee.OperationalError:
        print("Room table already exists.")

    
    temple_data   = { "name" : "temple"   }
    cemetery_data = { "name" : "cemetery" }

    for room in [ temple_data, cemetery_data ]:
        r = Room(**room)
        r.save()

    temple_room   = Room.get(Room.name == "temple")
    cemetery_room = Room.get(Room.name == "cemetery")

    temple_room.south   = cemetery_room
    cemetery_room.north = temple_room

    temple_room.save()
    cemetery_room.save()

    temple_room = Room.get(Room.name == "temple")

    print("temple_room.south_id   : %d" % temple_room.south_id)
    
    print("temple_room            : %s" % temple_room)
    print("temple_room.south      : %s" % temple_room.south)
    print("temple_room.south.north: %s" % temple_room.south.north)

    

        
