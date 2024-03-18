from adventure import Thing, Room, Door, Player, Game

burrow = Room("Your Burrow")
basement = Room("Your Basement")
front_yard = Room("Your Front Yard")

front_door = Door("Front Door")
trap_door = Door("Trap Door", concealed=True)
burrow.exit_to('n', front_yard, front_door)
burrow.exit_to('d', basement, trap_door)

class Rug(Thing):
    def move(self):
        if trap_door.concealed:
            print("Moving the rug reveals a trap door to the basement.")
            trap_door.concealed = False
        else:
            super().move()

rug = Rug("a rug", fixed=True)
burrow.contents.add(rug)
lantern = Thing("a lantern")
burrow.contents.add(lantern)


player = Player()
player.location = burrow

class FrogGame(Game):
    def welcome(self):
        print("""\
You are in a burrow, but not just any burrow.  The burrow you reside in is in
fact the estate of Von Frogerick III, who just so happens to be your great
great grandfather.  The immense and fascinating history of your lineage matters
not though, for you are hungry.  You should find a fly to eat.
""")

game = FrogGame(player)

if __name__ == '__main__':

    game.play()
