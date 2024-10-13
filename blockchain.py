import os
import struct
import time
import uuid
import hashlib
from block import Block

class Blockchain:
    def __init__(self):
        self.blocks = []
        self.blockchain_file = os.getenv("BCHOC_FILE_PATH", "blockchain.bin")  # Use environment variable for file path
        self.load_chain()

    def load_chain(self):
        if os.path.exists(self.blockchain_file):
            with open(self.blockchain_file, "rb") as f:
                while True:
                    block_data = f.read(144)  # Adjust block size if necessary
                    if not block_data:
                        break
                    self.blocks.append(Block.deserialize(block_data))
            
        # Only call init if no blocks were loaded (i.e., a completely new blockchain)
        if not self.blocks:
            self.init()


    def init(self):
        prev_hash = b'\x00' * 32
        timestamp = time.time()  # Get the current time for the timestamp
        case_id = b'\x00' * 32
        evidence_id = b'\x00' * 32
        state = b'INITIAL\x00\x00\x00\x00\x00'
        creator = b'\x00' * 12
        owner = b'\x00' * 12
        data = b'Initial block\0'
        
        # Calculate the data length
        data_length = len(data)


        if not self.blocks:
            print("> Blockchain file not found. Created INITIAL block.")  # Print message for new block creation
        else:
            print("> Blockchain file found with INITIAL block.")  # Print message for existing block

        genesis_block = Block(
            previous_hash=prev_hash,
            timestamp=timestamp,
            case_id=case_id,
            evidence_id=evidence_id,
            state=state,
            creator=creator,
            owner=owner,
            data=data
        )
        
        # Set the data length for the genesis block
        genesis_block.data_length = data_length

        # Add the block to the chain
        self.blocks.append(genesis_block)
        
        # Save the chain to the blockchain file
        self.save_chain()


    def save_chain(self):
        with open(self.blockchain_file, "wb") as f:
            for block in self.blocks:
                f.write(block.serialize())

    def display_chain(self):
        for index, block in enumerate(self.blocks):
            print(f"Block {index}:")
            print(f"  Previous Hash: {block.previous_hash.hex()}")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Case ID: {block.case_id.hex()}")
            print(f"  Evidence ID: {block.evidence_id.hex()}")
            print(f"  State: {block.state.decode('utf-8').strip()}")
            print(f"  Creator: {block.creator.hex()}")
            print(f"  Owner: {block.owner.hex()}")
            print(f"  Data Length: {block.data_length}")
            print(f"  Data: {block.data.decode('utf-8')}\n")

    def calc_previous_hash(self):
        return self.blocks[self.blocks.siz]

    def add_block(self, previous_hash: bytes, timestamp: float, case_id: bytes,  evidence_id: bytes, state: bytes, creator: bytes, owner: bytes, data: bytes):
        return


