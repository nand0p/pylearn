COMMANDS = { 'go', 'move', 'use', 'examine', 'open', 'close', 'inventory' }

DIRECTIONS = set()
REVERSE_DIRECTION = {}

for fwd, rev in (('n', 's'), ('e', 'w'), ('u', 'd')):
    DIRECTIONS.add(fwd)
    DIRECTIONS.add(rev)
    REVERSE_DIRECTION[fwd] = rev
    REVERSE_DIRECTION[rev] = fwd

class CantSee(Exception):
    pass

class Thing:
    def __init__(self, short_description, **kwargs):
        self.short_description = short_description
        self.long_description = None
        self.concealed = False
        self.scenery = False
        self.fixed = False
        self.openable = False

        for key, value in kwargs.items():
            if not key in self.__dict__:
                raise ValueError("Unrecognized argument: "+key)
            self.__dict__[key] = value

    def description(self):
        return self.short_description

    def examine(self):
        if self.long_description:
            print(self.long_description)
        else:
            print("There is nothing special about it")

    def move(self):
        if self.fixed:
            print("You can't move it")
        else:
            print("You move it a bit.")


class Container(Thing):
    def __init__(self, short_description, **kwargs):
        self.contents = {}
        self.openable = True
        self.open = False
        self.transparent = False

        super().__init__(short_description, **kwargs)

    def containing():
        if self.contents:
            return ", ".join(item.description() for item in self.contents())
        return "nothing"


    def description(self):
        text = self.short_description
        if self.openable:
            if self.open:
                text += " (which is closed)"
            else:
                text += " (which is open)"

        if self.open or self.transparent:
            if self.contents:
                text += "(containing " + self.containing() + ")"

        return description


class Door(Thing):
    def __init__(self, short_description, **kwargs):

        self.lockable = False
        self.locked = False
        self.key = None
        self.connects = {}

        super().__init__(short_description, **kwargs)

        self.fixed = True
        self.closed = True

class Room(Thing):

    def __init__(self, name, **kwargs):
        self.exits = {}
        self.visited = False
        self.contents = set()

        super().__init__(name, **kwargs)

    def exit_to(self, direction, destination, door=None):
        reverse = REVERSE_DIRECTION[direction]

        if door:
            door.connects[direction] = destination
            door.connects[reverse] = self
            self.exits[direction] = door
            destination.exits[reverse] = door
        else:
            self.exits[direction] = destination
            destination.exits[reverse] = self

    def enter(self):
        print("Location:", self.short_description)
        if not self.visited:
            self.describe()
            self.visited = True

    def visible_things(self):
        return [item for item in self.contents if not item.concealed]

    def describe(self):
        if self.long_description:
            print(self.long_description)
            print()

        items = [item for item in self.visible_things()  if not item.scenery]

        for item in items:
            if item.concealed or item.scenery:
                continue

        if items:
            print("You see:")
            for item in items:
                print("   ", item.description())

class Player(Container):
    def __init__(self):
        super().__init__("yourself")
        self.long_description = "As good looking as ever."

        self.openable = False
        self.location = None
        self.alive = True

    def inventory(self):
        if self.contents:
            print("You are carring:")
            for item in self.contents:
                print("   ", item.description)
        else:
            print("You have nothing.")

    def go(self, direction):
        destination = self.location.exits.get(direction, None)
        if isinstance(destination, Door):
            door = destination
            destination = door.connects[direction]
            if door.concealed:
                destination = None
            elif door.closed:
                if door.locked:
                    print("You'd need to unlock the door first")
                    return
                print("First opening the", door.short_description)

        if destination:
            self.location = destination
            destination.enter()
        else:
            print("You can't go that way")

class Game:
    def __init__(self, protagonist):
        self.player = protagonist
        self.game_over = False
        self.turns = 0

    def welcome(self):
        print("A text adventure game.")

    def help(self):
        print("Examine everything.")

    def get_action(self):
        while True:
            command = input("\n> ").lower().split()

            if command:
                if len(command) == 1:
                    if command[0] in DIRECTIONS:
                        command.insert(0, 'go')
                    if command[0] == 'i':
                        command[0] = 'inventory'

                if command == ['inventory']:
                    self.player.inventory()

                elif command == ['help']:
                    self.help()

                elif command[0] == 'go':
                    if len(command) == 2 and command[1] in DIRECTIONS:
                        return command
                    else:
                        print("I'm sorry; go where?")

                elif command[0] in COMMANDS:
                    return command

                else:
                    print("I don't understand")

    def go(self, direction):
        self.player.go(direction)

    def item(self, thing):
        items = self.player.location.visible_things()
        for item in items:
            if thing in item.short_description:
                return item
        raise CantSee(thing)

    def move(self, thing):
        item = self.item(thing)
        item.move()        

    def perform_action(self, command):
        if command[0] == 'go' and len(command) == 2:
            self.go(command[1])
        elif command[0] == 'move' and len(command) == 2:
            self.move(command[1])
        else:
            print("Command not implemented")


    def play(self):
        self.welcome()

        self.player.location.enter()

        while not self.game_over:
            command = self.get_action()
            try:
                self.perform_action(command)
                self.turns += 1
            except CantSee as thing:
                print("You don't see a", thing)

        if not self.player.alive:
            print("You have died.")
        else:
            print("Game over.")
