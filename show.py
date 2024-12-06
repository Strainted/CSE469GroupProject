import os
import struct
from collections import namedtuple
from add import decrypt_data, AES_KEY

# Define the block format for struct unpacking
BLOCK_FORMAT = struct.Struct("32s d 32s 32s 12s 12s 12s I")


def show_cases(file_path):
    # Check if the blockchain file exists
    if not os.path.exists(file_path):
        print("Error: Blockchain file does not exist.")
        sys.exit(1)

    # Initialize a set to store unique case IDs
    unique_cases = set()

    try:
        with open(file_path, 'rb') as f:
            while True:
                # Read the block header
                head = f.read(BLOCK_FORMAT.size)
                if not head:
                    break  # End of file

                # Check for incomplete block header
                if len(head) < BLOCK_FORMAT.size:
                    print("Error: Incomplete block header.")
                    sys.exit(1)

                # Unpack the block header
                block_head = namedtuple(
                    'Block_Head',
                    'prev_hash timestamp case_id evidence_id state creator owner data_length'
                )._make(BLOCK_FORMAT.unpack(head))

                # Skip the genesis block (case_id is all zeros)
                if block_head.case_id == b'\x00' * 32:
                    continue

                # Decrypt and store unique case IDs only if the state is valid
                try:
                    state_str = block_head.state.rstrip(b'\x00').decode()
                    if state_str not in ['DISPOSED', 'DESTROYED', 'RELEASED']:
                        decrypted_case_id = decrypt_data(block_head.case_id, AES_KEY).hex()
                        unique_cases.add(decrypted_case_id)
                except Exception:
                    print("Error: Failed to decrypt case ID.")
                    sys.exit(1)

                # Skip block data
                f.read(block_head.data_length)

        # Display unique case IDs
        print("Displaying all cases:")
        for i, case_id in enumerate(sorted(unique_cases), start=1):  # Sorting for consistent test output
            print(f"- Case {i}: {case_id}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def show_items(file_path, case_id=None):
    """
    Display all items associated with a specific case ID.
    """
    if not os.path.exists(file_path):
        print("Blockchain file not found.")
        return

    items = []  # List to store items belonging to the specified case ID

    with open(file_path, 'rb') as f:
        while True:
            # Read block header
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break

            block_head = namedtuple(
                'Block_Head',
                'prev_hash timestamp case_id evidence_id state creator owner data_length'
            )._make(BLOCK_FORMAT.unpack(head))

            # Read block data (skipping over data length bytes)
            data_length = block_head.data_length
            f.read(data_length)

            # Decrypt the case ID and item ID
            decrypted_case_id = decrypt_data(block_head.case_id, AES_KEY)
            decrypted_item_id = decrypt_data(block_head.evidence_id, AES_KEY)

            # Check if the case ID matches
            if case_id is None or decrypted_case_id.hex() == case_id:
                items.append(int.from_bytes(decrypted_item_id, byteorder='big'))

    # Display items in the required format
    print("Displaying items:")
    for idx, item in enumerate(items, start=1):
        print(f"- Item {idx}: {item}")


def show_history(file_path, item_id=None, num_entries=None, reverse=False, password=None):
    """
    Display the blockchain history for a specific item ID, or for all items if item_id is not provided.
    """
    if not os.path.exists(file_path):
        print("Blockchain file not found.")
        return

    history = []  # List to store the history of actions

    with open(file_path, 'rb') as f:
        while True:
            # Read block header
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break

            block_head = namedtuple(
                'Block_Head',
                'prev_hash timestamp case_id evidence_id state creator owner data_length'
            )._make(BLOCK_FORMAT.unpack(head))

            # Read block data (skipping over data length bytes)
            data_length = block_head.data_length
            f.read(data_length)

            # Decrypt the item ID
            decrypted_item_id = decrypt_data(block_head.evidence_id, AES_KEY)
            item_id_int = int.from_bytes(decrypted_item_id, byteorder='big')

            # Add the block to history if it matches the item ID or if no specific item ID is requested
            if item_id is None or item_id == item_id_int:
                history.append({
                    'case_id': decrypt_data(block_head.case_id, AES_KEY).hex(),
                    'item_id': item_id_int,
                    'action': block_head.state.rstrip(b'\x00').decode(),
                    'time': datetime.fromtimestamp(block_head.timestamp).isoformat(),
                })

    # Reverse history if requested
    if reverse:
        history.reverse()

    # Limit the number of entries if num_entries is provided
    if num_entries:
        history = history[:num_entries]

    # Display history in the required format
    print("Displaying history:")
    for entry in history:
        print(f"> Case: {entry['case_id']}")
        print(f"> Item: {entry['item_id']}")
        print(f"> Action: {entry['action']}")
        print(f"> Time: {entry['time']}")

