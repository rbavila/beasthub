ESC = 0x1a
TYPE_MODE_AC = 0x31
TYPE_MODE_S_SHORT = 0x32
TYPE_MODE_S_LONG = 0x33

class BEASTParser:
    STATE_OUT_OF_SYNC = 0
    STATE_TS = 1
    STATE_RSSI = 2
    STATE_TYPE = 3
    STATE_PAYLOAD = 4

    def __init__(self, pdu_queue):
        self.pdu_queue = pdu_queue
        self.state = self.STATE_OUT_OF_SYNC
        self.current_pdu = None
        self.current_type = None
        self.field_bytes_to_go = None
        self.escaped = False

    def feed(self, bytes):
        for b in bytes:
            if self.state == self.STATE_OUT_OF_SYNC:
                if b == ESC:
                    self.current_pdu = bytearray([ESC])
                    self.state = self.STATE_TYPE
            else:
                self.current_pdu.append(b)
                if self.state == self.STATE_TYPE:
                    if b == TYPE_MODE_AC \
                            or b == TYPE_MODE_S_SHORT \
                            or b == TYPE_MODE_S_LONG:
                        self.current_type = b
                        self.field_bytes_to_go = 6
                        self.state = self.STATE_TS
                    else:
                        self.state = self.STATE_OUT_OF_SYNC
                elif not self.escaped and b == ESC:
                    self.escaped = True
                else:
                    if self.escaped:
                        self.escaped = False
                        if b != ESC:
                            self.state = self.STATE_OUT_OF_SYNC
                            continue
                    if self.state == self.STATE_TS:
                        self.field_bytes_to_go -= 1
                        if self.field_bytes_to_go == 0:
                            self.state = self.STATE_RSSI
                    elif self.state == self.STATE_RSSI:
                        if self.current_type == TYPE_MODE_AC:
                            self.field_bytes_to_go = 2
                        elif self.current_type == TYPE_MODE_S_SHORT:
                            self.field_bytes_to_go = 7
                        else:
                            self.field_bytes_to_go = 14
                        self.state = self.STATE_PAYLOAD
                    elif self.state == self.STATE_PAYLOAD:
                        self.field_bytes_to_go -= 1
                        if self.field_bytes_to_go == 0:
                            self.pdu_queue.put(self.current_pdu)
                            self.state = self.STATE_OUT_OF_SYNC
