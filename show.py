import os
import struct
import hashlib
from datetime import datetime
from collections import namedtuple
from add import decrypt_data, AES_KEY
from error import *
from init import GENESIS_BLOCK, create_block

BLOCK_FORMAT = struct.Struct("32s d 32s 32s 12s 12s 12s I")

def show_cases(file_path):
    """
    Displays all cases present in the blockchain.
    """
    if not os.path.exists(file_path):
        print("Blockchain file does not exist.")
        sys.exit(1)

    cases = {}
    with open(file_path, 'rb') as f:
        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break  # End of file
            curr_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')._make(BLOCK_FORMAT.unpack(head))
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)

            # Decrypt and collect case information
            decrypted_case_id = decrypt_data(curr_head.case_id, AES_KEY)
            decrypted_evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY)
            if decrypted_case_id != b'\0' * 16:  # Skip Genesis Block
                cases[decrypted_case_id] = data.decode().rstrip('\x00')

    print("Displaying all cases:")
    for idx, case in enumerate(cases.values(), start=1):
        print(f"- Case {idx}: {case}")

def show_items(file_path, case_id=None):
    """
    Displays all items for a given case ID.
    """
    if not os.path.exists(file_path):
        print("Blockchain file does not exist.")
        sys.exit(1)

    items = []
    with open(file_path, 'rb') as f:
        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break  # End of file
            curr_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')._make(BLOCK_FORMAT.unpack(head))
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)

            # Match items based on the provided case ID
            decrypted_case_id = decrypt_data(curr_head.case_id, AES_KEY)
            decrypted_evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY)
            if case_id and decrypted_case_id == case_id.encode():
                items.append(decrypted_evidence_id.decode().rstrip('\x00'))

    print("Displaying items:")
    for idx, item in enumerate(items, start=1):
        print(f"- Item {idx}: {item}")

def show_history(file_path, item_id=None, num_entries=None, reverse=False, password=None):
    """
    Displays the history of a specific item or the entire blockchain.
    """
    if not os.path.exists(file_path):
        print("Blockchain file does not exist.")
        sys.exit(1)

    history = []
    with open(file_path, 'rb') as f:
        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break  # End of file
            curr_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')._make(BLOCK_FORMAT.unpack(head))
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)

            decrypted_case_id = decrypt_data(curr_head.case_id, AES_KEY)
            decrypted_evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY)
            action = curr_head.state.rstrip(b'\x00').decode()
            timestamp = datetime.fromtimestamp(curr_head.timestamp).isoformat()

            if item_id:
                decrypted_item_id = int.from_bytes(decrypted_evidence_id, byteorder='big')
                if decrypted_item_id == item_id:
                    history.append({
                        'case': decrypted_case_id,
                        'item': decrypted_item_id,
                        'action': action,
                        'timestamp': timestamp
                    })
            else:
                history.append({
                    'case': decrypted_case_id,
                    'item': decrypted_evidence_id.decode(),
                    'action': action,
                    'timestamp': timestamp
                })

    # Apply reverse order if specified
    if reverse:
        history.reverse()

    # Apply limit to the number of entries
    if num_entries:
        history = history[:num_entries]

    # Output history
    for entry in history:
        print(f"> Case: {entry['case']}")
        print(f"> Item: {entry['item']}")
        print(f"> Action: {entry['action']}")
        print(f"> Time: {entry['timestamp']}")

