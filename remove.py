import os
import struct
import tempfile
from add import BLOCK_FORMAT, GENESIS_HASH, decrypt_data, AES_KEY, validate

def remove_block(file_path, evidence_id):
    if not os.path.exists(file_path):
        print("Blockchain file does not exist.")
        return

    # Open the blockchain file
    with open(file_path, 'rb') as f, tempfile.NamedTemporaryFile(delete=False) as tempf:
        block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')
        block_data = namedtuple('Block_Data', 'data')

        found = False
        while True:
            head = f.read(BLOCK_FORMAT.size)
            if not head:
                break
            curr_head = block_head._make(BLOCK_FORMAT.unpack(head))

            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)
            curr_data = block_data._make(DATA_FORMAT.unpack(data))

            # Decrypt the evidence ID
            decrypted_evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY).hex()

            if decrypted_evidence_id == evidence_id:
                found = True
                print(f"Block with Evidence ID {evidence_id} removed.")
                continue

            # Write the block to the temporary file if it doesn't match
            tempf.write(head)
            tempf.write(data)

    if not found:
        print(f"No block with Evidence ID {evidence_id} found.")
        os.remove(tempf.name)  # Remove temp file if no changes were made
        return

    # Replace the old blockchain file with the new one
    os.replace(tempf.name, file_path)
    print("Blockchain file updated successfully.")

if __name__ == "__main__":
    file_path = input("Enter blockchain file path: ").strip()
    evidence_id = input("Enter evidence ID to remove (in hexadecimal format): ").strip()
    remove_block(file_path, evidence_id)
