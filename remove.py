
import os
import struct
import hashlib
import uuid
from collections import namedtuple
from datetime import datetime
from add import create_block, encrypt_data, decrypt_data, get_passwords
from error import *

AES_KEY = b"R0chLi4uLi4uLi4="
BLOCK_FORMAT = struct.Struct("32s d 32s 32s 12s 12s 12s I")

def remove_item(item_id, reason, password, owner, file_path):
    if not os.path.exists(file_path):
        print("Error: Blockchain file does not exist.", file=sys.stderr)
        sys.exit(1)

    # Verify creator's password
    passwords = get_passwords()
    if password != passwords["CREATOR"]:
        print("Error: Invalid password for removal.", file=sys.stderr)
        invalid_password()

    block_size = BLOCK_FORMAT.size
    found = False
    case_id = None
    creator = None
    prev_hash = b'\0' * 32

    with open(file_path, 'rb') as f:
        # Move to the end of the file
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        if file_size <= block_size + 14:  # Genesis Block size
            print("Error: No evidence blocks found in Blockchain.", file=sys.stderr)
            sys.exit(1)

        # Traverse the file in reverse order
        while file_size > 0:
            # Seek to the beginning of the current block
            file_size -= block_size
            f.seek(file_size, os.SEEK_SET)

            # Read the block header
            head = f.read(block_size)
            curr_head = namedtuple('Block_Head', 'prev_hash timestamp case_id item_id state creator owner data_length')._make(BLOCK_FORMAT.unpack(head))

            # Read the block data
            data_length = curr_head.data_length
            file_size -= data_length
            f.seek(file_size, os.SEEK_SET)
            data = f.read(data_length)

            # Decrypt and compare item_id
            decrypted_item_id = decrypt_data(curr_head.item_id, AES_KEY)
            item_id_int = int.from_bytes(decrypted_item_id, byteorder='big')

            if item_id_int == item_id:
                # Debugging output


                # Check the state
                if curr_head.state.rstrip(b'\x00') == b'CHECKEDIN':
                    found = True
                    case_id = curr_head.case_id
                    creator = curr_head.creator
                    prev_hash = hashlib.sha256(head + data).digest()
                else:
                    print("Error: Item is not in a removable state (CHECKEDIN).", file=sys.stderr)
                    sys.exit(1)

                break  # Exit loop after processing the last block for this item

    if not found:
        print("Error: Item ID not found in Blockchain.", file=sys.stderr)
        sys.exit(1)

    # Create the removal block
    now = datetime.now()
    data = None
    if not owner:
        owner_data = curr_head.owner  # Use owner from the last block
    else:
        owner_data = owner.encode().ljust(12, b'\x00')[:12]

    data = b""
    block_data = {
        'prev_hash': b'\0',
        #'prev_hash': prev_hash,
        'timestamp': datetime.timestamp(now),
        'case_id': case_id,
        'evidence_id': encrypt_data(item_id.to_bytes(16, byteorder='big'), AES_KEY),
        'state': reason.encode().ljust(12, b'\x00')[:12],
        'creator': creator,
        'owner': owner_data,
        'd_length': len(data),
        'data': data,
    }

    new_block = create_block(block_data)

    # Append the block
    with open(file_path, 'ab') as f:
        f.write(new_block)
    print(f"Case: {uuid.UUID(bytes=decrypt_data(case_id, AES_KEY))}")
    print(f"Removed item: {item_id}")
    print(f"Reason: {reason}")
    print(f"Time of action: {datetime.now().isoformat()}Z")