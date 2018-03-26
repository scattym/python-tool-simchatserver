

class Command(object):
    def __init__(self, direction, payload=None):
        self.payload = payload
        self.direction = direction

    def __repr__(self):
        return self.payload

    def __str__(self):
        return self.payload