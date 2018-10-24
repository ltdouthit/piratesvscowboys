import json

FILLER = "^"
INSTRUCTION_LENGTH = 1024


class HandleTraffic:

    def get_update(self, socket):
        chunks = []
        bytes_received = 0
        while bytes_received < INSTRUCTION_LENGTH:
            chunk = socket.recv(
                min(INSTRUCTION_LENGTH - bytes_received,
                    INSTRUCTION_LENGTH * 2)
            )
            if chunk == b"":
                raise RuntimeError("Socket is broken on getting!")
            chunks.append(chunk)
            bytes_received = bytes_received + len(chunk)
        bytes_data = b"".join(chunks)
        return self.parse_bytes_to_json(bytes_data)

    def parse_bytes_to_json(self, bytes_data):
        bytes_data = bytes_data.decode().replace(FILLER, "")
        bytes_data = json.loads(bytes_data)
        return bytes_data

    def send_update(self, socket, data):
        if not data:
            data = [{"method": "do_nothing", "player_address": None}]
        bytes_data = self.parse_json_to_bytes(data)
        bytes_sent = 0
        while bytes_sent < INSTRUCTION_LENGTH:
            sent = socket.send(bytes_data[bytes_sent:])
            if sent == 0:
                raise RuntimeError("Socket is broken on sending!")
            bytes_sent += sent
        return []

    def parse_json_to_bytes(self, json_data):
        json_data = json.dumps(json_data)
        count = (INSTRUCTION_LENGTH - len(json_data)) / 2
        if count.is_integer():
            extra = ""
        else:
            extra = FILLER
        count = int(count)
        filler_bytes = FILLER * count
        bytes_data = (filler_bytes + json_data + filler_bytes + extra).encode()
        return bytes_data

    def execute(self, player_address, method, args=None, kwargs=None):
        method = getattr(self, method)
        args = args or []
        kwargs = kwargs or {}
        method(player_address, *args, **kwargs)
