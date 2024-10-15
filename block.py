import struct
import hashlib
import time

class Block:
    def __init__(self, previous_hash: bytes, timestamp: float, case_id: str, 
                 evidence_id: int, state: str, creator: str, owner: str, 
                 data_length: int, data: bytes):
        
        self.previous_hash = self.pad_bytes(previous_hash, 32)
        self.timestamp = timestamp
        self.case_id = self.pad_string(case_id, 32)
        self.evidence_id = self.pad_string(str(evidence_id), 32)  # Convert int to string, then pad
        self.state = self.pad_string(state, 12)
        self.creator = self.pad_string(creator, 12)
        self.owner = self.pad_string(owner, 12)
        self.data_length = data_length
        self.data = data

    @staticmethod
    def pad_string(value: str, length: int) -> bytes:
        if isinstance(value, bytes):  # Check if value is already bytes
            return value.ljust(length, b'\x00')
        return value.encode().ljust(length, b'\x00')

    @staticmethod
    def pad_bytes(value: bytes, length: int) -> bytes:
        return value.ljust(length, b'\x00')

    def serialize(self):
        # Pack the block data into bytes using the format string
        header = struct.pack(
            "32s d 32s 32s 12s 12s 12s I",
            self.previous_hash,
            self.timestamp,
            self.case_id,
            self.evidence_id,
            self.state,
            self.creator,
            self.owner,
            self.data_length
        )
        
        return header + self.data  # Append the variable length data
    
    @classmethod
    def deserialize(cls, data):
        if len(data) < 144:
            raise ValueError("Data is too short to be a valid block")

        unpacked_data = struct.unpack(
            "32s d 32s 32s 12s 12s 12s I", 
            data[:144]
        )
        previous_hash, timestamp, case_id, evidence_id, state, creator, owner, data_length = unpacked_data
        
        # Decode strings and strip padding
        case_id = case_id.decode().rstrip('\x00')
        evidence_id = evidence_id.decode().rstrip('\x00')
        state = state.decode().rstrip('\x00')
        creator = creator.decode().rstrip('\x00')
        owner = owner.decode().rstrip('\x00')

        block_data = data[144:144 + data_length]
        
        return cls(previous_hash, timestamp, case_id, evidence_id, state, creator, owner, data_length, block_data)
