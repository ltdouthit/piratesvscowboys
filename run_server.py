from sys import argv

from pirates_server.server import MatchMaker, HOST, PORT


if __name__ == "__main__":
    host = HOST
    try:
        port = int(argv[1])
    except IndexError:
        port = PORT
    try:
        host = int(argv[2])
    except IndexError:
        host = HOST
    server = MatchMaker(host, port, listen=10)
    server.run()
