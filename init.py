import os
import struct
import argparse
from datetime import datetime
from collections import namedtuple
import sys
from error import *

GENESIS_BLOCK = {
    'prev_hash': b'0' * 32,          # 32 bytes
    'timestamp': 0.0,           # 08 bytes
    'case_id': b'0' * 32,            # 32 bytes
    'evidence_id': b'0' * 32,        # 32 bytes
    'state': b'INITIAL\0\0\0\0\0',   # 12 bytes
    'creator': b'\0' * 12,           # 12 bytes
    'owner': b'\0' * 12,             # 12 bytes
    'd_length': 14,                  # 04 bytes (integer)
    'data': b'Initial block\0',      # Data with length 14
}

def create_block(block_data):
    """Create a binary representation of a block."""
    block_format = '32s d 32s 32s 12s 12s 12s I 14s'
    return struct.pack(block_format, 
                       block_data['prev_hash'],
                       block_data['timestamp'],
                       block_data['case_id'],
                       block_data['evidence_id'],
                       block_data['state'],
                       block_data['creator'],
                       block_data['owner'],
                       block_data['d_length'],
                       block_data['data'])

def init(file_path):
    block_head_format = struct.Struct('32s d 32s 32s 12s 12s 12s I')
    block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')
    block_data = namedtuple('Block_Data', 'data')

    if not os.path.exists(file_path): #if no file create genesis block and add to file
        with open(file_path, 'wb') as f:
            genesis_block = create_block(GENESIS_BLOCK)
            f.write(genesis_block)

        print("Blockchain file not found. Created INITIAL block.")
    else: #file exists check if genesis block exists
        with open(file_path, 'rb') as f:
            first_block = f.read(struct.calcsize('32s d 32s 32s 12s 12s 12s I 14s'))
            if first_block != create_block(GENESIS_BLOCK):
                print("Genesis block not found. Appending the Genesis block.")
                with open(file_path, 'ab') as f_append:
                    genesis_block = create_block(GENESIS_BLOCK)
                    f_append.write(genesis_block)
            else:
                print("Genesis block already exists.")
    


