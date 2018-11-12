class Matchmaker:

    def __init__(self, client):
        print("Starting matchmaking.")
        self.client = client
        connection_data = self.client.get_from.get(block=True)
        self.token = connection_data["token"]
        self.is_admin = connection_data["is_admin"]
        if self.is_admin:
            input("PRESS ENTER TO START GAME")
            self.client.send_to.put({"start_game": True})
            self.client.send_local_instructions()
        else:
            print("WAITING ON ADMIN TO START GAME")

    def get_game_state(self):
        return self.client.get_from.get(block=True)
