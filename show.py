import os
import struct
import hashlib
from collections import namedtuple
from add import AES_KEY, decrypt_data

BLOCK_FORMAT = struct.Struct("32s d 32s 32s 12s 12s 12s I")

def show_item(item_id, file_path):
    if not os.path.exists(file_path):
        print("Blockchain file does not exist")
        return False

    found = False

    with open(file_path, 'rb') as f:
        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id item_id state creator owner data_length')
        block_data = namedtuple('Block_Data', 'data')

        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break
            curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)

            decrypted_item_id = decrypt_data(curr_head.item_id, AES_KEY)
            item_id_int = int.from_bytes(decrypted_item_id, byteorder='big')

            if item_id_int == item_id:
                found = True
                decrypted_case_id = decrypt_data(curr_head.case_id, AES_KEY).decode().strip('\0')
                print(f"Case ID: {decrypted_case_id}")
                print(f"Item ID: {item_id}")
                print(f"State: {curr_head.state.rstrip(b'\x00').decode()}")
                print(f"Creator: {curr_head.creator.rstrip(b'\x00').decode()}")
                print(f"Owner: {curr_head.owner.rstrip(b'\x00').decode()}")
                print(f"Timestamp: {curr_head.timestamp}")
                print(f"Data: {data.decode().strip('\0')}")
                break

    if not found:
        print(f"Item with ID {item_id} not found in the blockchain.")
    return found


def show_case(case_id, file_path):
    if not os.path.exists(file_path):
        print("Blockchain file does not exist")
        return False

    found = False
    case_items = []

    with open(file_path, 'rb') as f:
        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id item_id state creator owner data_length')
        block_data = namedtuple('Block_Data', 'data')

        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break
            curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            f.read(curr_head.data_length)

            decrypted_case_id = decrypt_data(curr_head.case_id, AES_KEY).decode().strip('\0')

            if decrypted_case_id == case_id:
                found = True
                decrypted_item_id = decrypt_data(curr_head.item_id, AES_KEY).decode()
                case_items.append(decrypted_item_id)

    if found:
        print(f"Case ID: {case_id}")
        print("Items:")
        for item in case_items:
            print(f" - Item ID: {item}")
    else:
        print(f"No case found with ID {case_id}")

    return found
