import struct
import os
import hashlib
import time

class Block:
    def __init__(self, previous_hash: bytes, timestamp: float, case_id: bytes, 
                 evidence_id: bytes, state: bytes, creator: bytes, owner: bytes, data: bytes):
        self.previous_hash = previous_hash
        self.timestamp = timestamp  # Use the provided timestamp
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.state = state
        self.creator = creator
        self.owner = owner
        self.data = data  # Store the data directly
        self.data_length = len(data)

    def serialize(self):
        return struct.pack(
            "32s d 32s 32s 12s 12s 12s I",
            self.previous_hash,
            self.timestamp,
            self.case_id,
            self.evidence_id,
            self.state,
            self.creator,
            self.owner,
            self.data_length
        ) + self.data  # Append the actual data after packing the structured fields
#ChatGPT
    @classmethod
    def deserialize(cls, data):
        unpacked_data = struct.unpack("32s d 32s 32s 12s 12s 12s I", data[:144])  # Change to 144 bytes
        previous_hash, timestamp, case_id, evidence_id, state, creator, owner, data_length = unpacked_data
        block_data = data[144:]  # Assuming data follows after the first 144 bytes
        return cls(previous_hash, timestamp, case_id, evidence_id, state, creator, owner, block_data)
