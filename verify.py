
import os
import sys
import struct
import hashlib
import uuid
from datetime import datetime
from collections import namedtuple
from add import decrypt_data, AES_KEY, BLOCK_FORMAT
from error import *
from init import GENESIS_BLOCK, create_block

def verify_blockchain(file_path):
    if not os.path.exists(file_path):
        print("Error: Blockchain file does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(file_path, 'rb') as f:
        prev_hash = b'\x00' * 32  # For the Genesis block
        block_index = 0
        last_timestamp = None

        while True:
            # Read block header
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break  # End of file
            if len(head) < BLOCK_FORMAT.size:
                print(f"Error: Incomplete block header at block index {block_index}.", file=sys.stderr)
                sys.exit(1)

            # Unpack block header
            try:
                block_head = namedtuple(
                    'Block_Head',
                    'prev_hash timestamp case_id evidence_id state creator owner data_length'
                )._make(BLOCK_FORMAT.unpack(head))
            except struct.error as e:
                print(f"Error: Failed to unpack block header at index {block_index}: {e}", file=sys.stderr)
                sys.exit(1)

            # Read block data
            data_length = block_head.data_length
            data = f.read(data_length)
            if len(data) < data_length:
                print(f"Error: Incomplete block data at block index {block_index}.", file=sys.stderr)
                sys.exit(1)

            # Compute hash of the current block
            curr_hash = hashlib.sha256(head + data).digest()

            # Validate block
            if block_index == 0:
                # Genesis block validation
                # Check Prev_hash
                if block_head.prev_hash != b'\x00' * 32:
                    print("Error: Genesis block has invalid prev_hash.", file=sys.stderr)
                    sys.exit(1)
                # Check Timestamp
                if block_head.timestamp != 0.0:
                    print("Error: Genesis block has invalid timestamp.", file=sys.stderr)
                    sys.exit(1)
                # Check State
                state_str = block_head.state.rstrip(b'\x00').decode()
                if state_str != 'INITIAL':
                    print("Error: Genesis block has invalid state.", file=sys.stderr)
                    sys.exit(1)
                # Check Data Length
                if block_head.data_length != 14:
                    print("Error: Genesis block has invalid data length.", file=sys.stderr)
                    sys.exit(1)
                # Optionally check other fields as needed
            else:
                # Check if prev_hash matches the hash of the previous block
                if block_head.prev_hash != prev_hash:
                    print(f"Error: Invalid prev_hash at block index {block_index}.", file=sys.stderr)
                    sys.exit(1)
                # Check if timestamp is not earlier than the previous block's timestamp
                if last_timestamp is not None and block_head.timestamp < last_timestamp:
                    print(f"Error: Timestamps are not in chronological order at block index {block_index}.",
                          file=sys.stderr)
                    sys.exit(1)

            # Validate state
            state_str = block_head.state.rstrip(b'\x00').decode()
            allowed_states = ['INITIAL', 'CHECKEDIN', 'CHECKEDOUT', 'DISPOSED', 'DESTROYED', 'RELEASED']
            if state_str not in allowed_states:
                print(f"Error: Invalid state '{state_str}' at block index {block_index}.", file=sys.stderr)
                sys.exit(1)

            # Validate creator and owner lengths
            if len(block_head.creator) != 12 or len(block_head.owner) != 12:
                print(f"Error: Invalid creator or owner length at block index {block_index}.", file=sys.stderr)
                sys.exit(1)

            # Decrypt and validate case_id and evidence_id
            try:
                decrypted_case_id = decrypt_data(block_head.case_id, AES_KEY)
                if len(decrypted_case_id) != 16:
                    print(f"Error: Invalid decrypted case_id length at block index {block_index}.", file=sys.stderr)
                    sys.exit(1)
                # Validate case_id as UUID
                if block_index != 0 or decrypted_case_id != b'\x00' * 16:
                    uuid.UUID(bytes=decrypted_case_id)
            except Exception as e:
                print(f"Error: Failed to decrypt or validate case_id at block index {block_index}: {e}",
                      file=sys.stderr)
                sys.exit(1)

            try:
                decrypted_evidence_id = decrypt_data(block_head.evidence_id, AES_KEY)
                decrypted_evidence_id = decrypted_evidence_id[:4]
                if len(decrypted_evidence_id) != 4:
                    print(f"Error: Invalid decrypted evidence_id length at block index {block_index}.",
                          file=sys.stderr)
                    sys.exit(1)
                # Convert to integer
                int.from_bytes(decrypted_evidence_id, byteorder='big')
            except Exception as e:
                print(f"Error: Failed to decrypt or validate evidence_id at block index {block_index}: {e}",
                      file=sys.stderr)
                sys.exit(1)

            # Update prev_hash and last_timestamp for next iteration
            prev_hash = curr_hash
            last_timestamp = block_head.timestamp
            block_index += 1

    # If we reach here, the blockchain is valid
    print("Blockchain is valid.")
    sys.exit(0)