
import os
import sys
from error import *
from datetime import datetime
from collections import namedtuple
from add import create_block, encrypt_data, decrypt_data
import struct
import hashlib
from checkout import verify_user
from add import create_block, encrypt_data, decrypt_data, get_passwords
import uuid


AES_KEY = b"R0chLi4uLi4uLi4="
BLOCK_FORMAT = struct.Struct("32s d 32s 32s 12s 12s 12s I")


def check_in(item_id, password, file_path):
    owner = verify_user(password)

    if not os.path.exists(file_path):
        print("Block chain file does not exist")

   

    prev_ids = []

    with open(file_path, 'rb') as f:
        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id item_id state creator owner data_length')
        block_data = namedtuple('Block_Data', 'data')
        found = False
        case_id = None
        checkedin = False

        prev_hash = ''
        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break
            curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
            prev_ids.append(curr_head.item_id)
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)
            curr_data = block_data._make(DATA_FORMAT.unpack(data))
            prev_hash = hashlib.sha256(head + data).digest()

            decrypted_item_id = decrypt_data(curr_head.item_id, AES_KEY)
            item_id_int = int.from_bytes(decrypted_item_id, byteorder='big')

            if item_id_int == item_id:
                found = True
                case_id = curr_head.case_id
                creator = curr_head.creator
                if curr_head.state.rstrip(b'\x00') in [b'CHECKEDOUT']:
                    checkedin = False

                if curr_head.state.rstrip(b'\x00') in [b'CHECKEDIN', b'DISPOSED', b'RELEASED',
                                                    b'DESTROYED']:  # double check this works after doing remove
                    checkedin = True
                    found = False

    if not found:
        if checkedin == True:
            print('Item previously checkedin cannot checkin')
            no_item_id()
        else:
            print("Item_id not found in Blockchain")
            no_item_id()

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    block_data = {
        'prev_hash': prev_hash,
        'timestamp': timestamp,
        'case_id': case_id,
        'evidence_id': encrypt_data(item_id.to_bytes(16, byteorder='big'), AES_KEY),
        'state': b'CHECKEDIN',
        'creator': creator,
        'owner': owner.encode(),
        'd_length': 0,
        'data': b''
    }

    new_block = create_block(block_data)

    with open(file_path, 'ab') as f:
        f.write(new_block)
        print(f"Case: {uuid.UUID(bytes=decrypt_data(case_id, AES_KEY))}")
        print(f"Checking out item: {item_id}")
        print("Status: CHECKEDIN")
        print(f"Time of action: {datetime.now().isoformat()}Z")

    return True