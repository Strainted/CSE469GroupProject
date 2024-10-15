import os
import struct
import time
import uuid
from Crypto.Cipher import AES
from block import Block
import hashlib
from datetime import datetime, timezone

AES_KEY = b"R0chLi4uLi4uLi4="

class Blockchain:
    def __init__(self):
        self.blocks = []
        self.blockchain_file = os.getenv("BCHOC_FILE_PATH", "blockchain.bin")  # Use environment variable for file path
        self.load_chain()
        self.init()

    
    def load_chain(self):
        if os.path.exists(self.blockchain_file):
            with open(self.blockchain_file, "rb") as f:
                while True:
                    block_data = f.read(144) 
                    if len(block_data) < 144:  
                        if block_data:  
                            print(f"Warning: Incomplete block read. Length: {len(block_data)}")
                        break  
                    try:
                        data_length = struct.unpack("I", block_data[140:144])[0]
                    except struct.error as e:
                        print(f"Error unpacking data_length: {e}")
                        break 
                    
                    total_bytes = 144 + data_length 
                    block_data += f.read(data_length)  
                    
                    if len(block_data) < total_bytes:
                        print(f"Warning: Expected {total_bytes} bytes, but read {len(block_data)} bytes.")
                        break
                    
                    self.blocks.append(Block.deserialize(block_data))  

    def init(self):
        prev_hash = b'\x00' * 32
        timestamp = datetime.now(timezone.utc).timestamp()
        case_id = b'\x00' * 32
        evidence_id = b'\x00' * 32
        state = b"INITIAL\x00\x00\x00\x00\x00"
        creator = b'\x00' * 12  
        owner = b'\x00' * 12  
        data_length = 14
        data = b"Initial block\x00"
        
        if not self.blocks:
            print("Blockchain file not found. Creating INITIAL block.")
            # Create the genesis block
            genesis_block = Block(
                previous_hash=prev_hash,
                timestamp=timestamp,
                case_id=case_id,
                evidence_id=evidence_id,
                state=state,
                creator=creator,
                owner=owner,
                data_length=data_length,
                data=data
            )

            # Add the block to the chain
            self.blocks.append(genesis_block)

            # Save the chain to the blockchain file
            self.save_chain()
        else:
            print("Blockchain file found with INITIAL block.")

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
        last_block = self.blocks[-1]
        return hashlib.sha256(last_block.serialize()).digest()
    


    def add_block(self, case_id, item_ids, password, creator_id):
        if not self.verify_password(creator_id, password):
            print("Incorrect Password")
            return
        
        for item_id in item_ids:
            if not self.is_unique_item_id(item_id):
                print("ID already exists")
                return
            
            prev_hash = self.calc_previous_hash()
            timestamp = datetime.now(timezone.utc).timestamp()

            state = b'CHECKEDIN' + b'\x00' * 4

            new_block = Block(
                previous_hash=prev_hash,
                timestamp=timestamp,
                case_id=case_id,
                evidence_id=item_id,
                state=state,
                creator=creator_id,
                owner=b'\x00' * 12,
                data_length=0,
                data=b''   
            )

            self.blocks.append(new_block)

            self.save_chain()
            self.display_chain()

        


    def verify_password(self, creator, password):
        return True
    
    def is_unique_item_id(self, item_id):
        return True