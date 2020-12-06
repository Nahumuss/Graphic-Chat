from Classes.BroadcastMessage import BroadcastMessage


class Message(BroadcastMessage):
    def __init__(self, time, source, data):
        super().__init__(data)
        self.time = time
        self.source = source

    def __str__(self):
        return f"[{self.time}] {self.source}: {self.data}"