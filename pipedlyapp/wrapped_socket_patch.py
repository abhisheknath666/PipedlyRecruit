import requests

def fileno(self):
    return self.socket.fileno()


def close(self):
    return self.connection.shutdown()


requests.pyopenssl.WrappedSocket.close = close
requests.pyopenssl.WrappedSocket.fileno = fileno
