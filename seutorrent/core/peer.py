class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __repr__(self):
        return "Peer <host: %s, port: %d>" % (self.host, self.port)
