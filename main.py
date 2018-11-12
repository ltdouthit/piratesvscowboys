import sys
import threading


class NetworkingThread(threading.Thread):

    def __init__(self, client):
        self.client = client
        super().__init__(target=client.run)

    def quit(self):
        self.client.stop()
        self.join()


def pyxel_setup():
    pyxel.init(250, 153, caption="Pirates vs Cowboys")
    pyxel.image(0).load(
        0, 0, "pirates_vs_cowboys/assets/cowboys/cowboy1_standing.png")
    pyxel.image(0).load(
        32, 0, "pirates_vs_cowboys/assets/cowboys/cowboy1_left.png")
    pyxel.image(0).load(
        64, 0, "pirates_vs_cowboys/assets/cowboys/cowboy1_right.png")
    pyxel.image(0).load(
        96, 0, "pirates_vs_cowboys/assets/cowboys/cowboy1_up.png")
    pyxel.image(1).load(
        51*0, 0, "pirates_vs_cowboys/assets/background/sky_tiles/skyTile0.png")
    pyxel.image(1).load(
        51*1, 0, "pirates_vs_cowboys/assets/background/sky_tiles/skyTile1.png")
    pyxel.image(1).load(
        51*2, 0, "pirates_vs_cowboys/assets/background/sky_tiles/skyTile2.png")
    pyxel.image(1).load(
        51*3, 0, "pirates_vs_cowboys/assets/background/ship_tiles/test_deck.png")
    pyxel.image(2).load(
        0, 0, "pirates_vs_cowboys/assets/background/ship_tiles/Crate0.png")


HOST = "localhost"
PORT = 5000

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        try:
            port = sys.argv[2]
        except IndexError:
            port = PORT
        from networking.server import Server
        server = Server(PORT)
        server.run()
    else:
        import pyxel
        from pirates_vs_cowboys.game import Game
        from pirates_vs_cowboys.matchmaker import Matchmaker
        from networking.client import Client
        client = Client(HOST, PORT)
        networking_thread = NetworkingThread(client)
        networking_thread.start()
        matchmaker = Matchmaker(client)
        players = matchmaker.get_game_state()
        pyxel_setup()
        game = Game(client, players, matchmaker.token, game_pyxel=pyxel)
        game.run()
        networking_thread.quit()
