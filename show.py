import os
import struct
import binascii
from init import *
from Crypto.Cipher import AES
from datetime import datetime
from add import BLOCK_FORMAT, GENESIS_HASH, decrypt_data, AES_KEY

def show_blocks(file_path):
    if not os.path.exists(file_path):
        print("Blockchain file does not exist.")
        return

    with open(file_path, 'rb') as f:
        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')
        block_data = namedtuple('Block_Data', 'data')

        print(f"{'Block Number':<15}{'Case ID':<40}{'Evidence ID':<40}{'State':<12}{'Timestamp':<30}{'Creator':<15}")
        print("-" * 140)

        block_number = 1
        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break
            curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
            
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)
            curr_data = block_data._make(DATA_FORMAT.unpack(data))

            # Decrypt fields for display
            case_id = decrypt_data(curr_head.case_id, AES_KEY).hex()
            evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY).hex()
            timestamp = datetime.fromtimestamp(curr_head.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            state = curr_head.state.decode().rstrip('\0')
            creator = curr_head.creator.decode().rstrip('\0')

            print(f"{block_number:<15}{case_id:<40}{evidence_id:<40}{state:<12}{timestamp:<30}{creator:<15}")
            block_number += 1

if __name__ == "__main__":
    file_path = input("Enter blockchain file path: ").strip()
    show_blocks(file_path)
