import os
import struct
import binascii
from collections import namedtuple
from Crypto.Cipher import AES
from datetime import datetime
import uuid
from add import BLOCK_FORMAT, decrypt_data, AES_KEY


class Show:
    def __init__(self):
        self.cases = []
        self.history = []
        self.items = []

    def add_case(self, case):
        self.cases.append(case)
        self.history.append(f"Added case: {case}")

    def add_item(self, item):
        self.items.append(item)
        self.history.append(f"Added item: {item}")

    def show_case(self):
        if self.cases:
            print("Displaying all cases:")
            for case in self.cases:
                print(f"- {case}")
        else:
            print("No cases to display.")

    def show_history(self):
        if self.history:
            print("History of actions:")
            for event in self.history:
                print(f"- {event}")
        else:
            print("No history to display.")

    def show_items(self):
        if self.items:
            print("Displaying items:")
            for item in self.items:
                print(f"- {item}")
        else:
            print("No items to display.")

    def show_items(self, file_path, case_uuid_str):
        if not os.path.exists(file_path):
            print("Blockchain file does not exist.")
            return

        requested_case_uuid = uuid.UUID(case_uuid_str)
        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')
        found_items = set()

        with open(file_path, 'rb') as f:
            while True:
                head = f.read(BLOCK_FORMAT.size)
                if not head:
                    break

                curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
                data = f.read(curr_head.data_length)

                state_str = curr_head.state.rstrip(b'\x00').decode()
                if curr_head.timestamp == 0.0 and state_str == "INITIAL":
                    continue
                decrypted_case_id = decrypt_data(curr_head.case_id, AES_KEY)
                if len(decrypted_case_id) < 16:
                    continue
                current_case_uuid = uuid.UUID(bytes=decrypted_case_id[:16])

                if current_case_uuid == requested_case_uuid:
                    decrypted_evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY)
                    if len(decrypted_evidence_id) < 4:
                        continue
                    evidence_id_int = int.from_bytes(decrypted_evidence_id[:4], 'big')
                    found_items.add(evidence_id_int)

        for item_id in found_items:
            print(item_id)

    def show_cases(self, file_path):
        if not os.path.exists(file_path):
            print("Blockchain file does not exist.")
            return

        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')
        unique_cases = set()

        with open(file_path, 'rb') as f:
            while True:
                head = f.read(BLOCK_FORMAT.size)
                if not head:
                    break

                curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
                data = f.read(curr_head.data_length)

                state_str = curr_head.state.rstrip(b'\x00').decode()
                if curr_head.timestamp == 0.0 and state_str == "INITIAL":
                    continue

                decrypted_case_id = decrypt_data(curr_head.case_id, AES_KEY)
                if len(decrypted_case_id) < 16:
                    continue

                case_uuid_bytes = decrypted_case_id[:16]
                try:
                    case_id_str = str(uuid.UUID(bytes=case_uuid_bytes))
                except ValueError:
                    continue

                unique_cases.add(case_id_str)

        if unique_cases:
            for case_id in unique_cases:
                print(f"{case_id}")
        else:
            print("No cases found.")

        return True
