from Classes.Message import Message
from datetime import datetime
from Classes.TwoWayDict import TwoWayDict

commands = TwoWayDict()
commands["demote"] = 1
commands["promote"] = 2
commands["kick"] = 3
commands["mute"] = 4
commands["unmute"] = 5
commands["whisper"] = 6
commands["login"] = 7
commands["register"] = 8
commands["disconnect"] = 9

class CommandMessage(Message):
    def __init__(self, time, source, destinations, data, command):
        super().__init__(time, source, data)
        self.destinations = destinations
        self.command = command

    def __str__(self):
        if self.command == commands["disconnect"]:
            return f"[{self.time}] {self.source} has {commands[self.command]}ed"
        if commands[self.command][-1] == 'e':
            return f"[{self.time}] {self.source} has {commands[self.command]}d you {self.data}"
        else:
            return f"[{self.time}] {self.source} has {commands[self.command]}ed you {self.data}"


def string_to_command(raw_message, source):
    command, value = raw_message.split(' ')
    if ' ' not in value:
        data = ''
        namesraw = value
    else:
        namesraw, data = value.split(' ')
    if ',' in namesraw:
        names = namesraw.split(',')
    else:
        names = [namesraw]
    timestemp = datetime.now()
    time = f'{timestemp.hour}:{timestemp.minute}'
    return CommandMessage(time, source, names, data, commands[command])