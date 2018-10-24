from sys import argv

from server import PVCS, HOST, PORT


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
    server = PVCS(host, port)
    print("pvcs server started on {}:{}.\n".format(host or "localhost", port))
    server.run()
