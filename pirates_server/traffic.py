import json

FILLER = "^"
INSTRUCTION_LENGTH = 256
DO_NOTHING_STR = "__DO_NOTHING__"
DO_NOTHING_BYTES = DO_NOTHING_STR.encode()

do_nothing_count = (INSTRUCTION_LENGTH - len(DO_NOTHING_STR)) / 2
if do_nothing_count.is_integer():
    do_nothing_extra = ""
else:
    do_nothing_extra = FILLER
do_nothing_count = int(do_nothing_count)
filler_bytes = FILLER * do_nothing_count
DO_NOTHING_INSTRUCTION = (
    filler_bytes + DO_NOTHING_STR + filler_bytes + do_nothing_extra
).encode()


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
        return self.parse_bytes_to_dict(bytes_data)

    def parse_bytes_to_dict(self, bytes_data):
        if DO_NOTHING_BYTES in bytes_data:
            return
        bytes_data = bytes_data.decode().replace(FILLER, "")
        bytes_data = json.loads(bytes_data)
        return bytes_data

    def send_update(self, socket, data):
        if not data:
            data = [DO_NOTHING_STR]
        for ins in data:
            bytes_data = self.parse_dict_to_bytes(ins)
            bytes_sent = 0
            while bytes_sent < INSTRUCTION_LENGTH:
                sent = socket.send(bytes_data[bytes_sent:])
                if sent == 0:
                    raise RuntimeError("Socket is broken on sending!")
                bytes_sent += sent
        return []

    def parse_dict_to_bytes(self, ins_dict):
        if ins_dict == DO_NOTHING_STR:
            return DO_NOTHING_INSTRUCTION
        dict_data = json.dumps(ins_dict)
        count = (INSTRUCTION_LENGTH - len(dict_data)) / 2
        if count.is_integer():
            extra = ""
        else:
            extra = FILLER
        count = int(count)
        filler_bytes = FILLER * count
        bytes_data = (filler_bytes + dict_data + filler_bytes + extra).encode()
        return bytes_data
