import os
import struct
import binascii
from collections import namedtuple
from Crypto.Cipher import AES
from datetime import datetime
from add import BLOCK_FORMAT, decrypt_data, AES_KEY
import uuid

def show_cases(file_path):
    firstBlock = True
    if not os.path.exists(file_path):
        print("Blockchain file does not exist.")
        return

    with open(file_path, 'rb') as f:
        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')
        block_data = namedtuple('Block_Data', 'data')

        prev_cases = set()
        while True:
            if firstBlock:
                firstBlock = False
                continue

            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break
            curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
            
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)
            curr_data = block_data._make(DATA_FORMAT.unpack(data))
            case_id = decrypt_data(curr_head.case_id, AES_KEY).hex()

            if len(case_id) == 32:
                case_id = str(uuid.UUID(case_id))
            else:
                print(f"Invalid case_id: {case_id}")
                continue


            evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY).hex()
            timestamp = datetime.fromtimestamp(curr_head.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            state = curr_head.state.decode().rstrip('\0')
            creator = curr_head.creator.decode().rstrip('\0')

            
            
            prev_cases.add(case_id)
    
    for case in prev_cases:
        print(f"Case: {case:<40}\n")

    return True
