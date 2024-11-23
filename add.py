import os
import sys
import uuid
import base64
import struct
import hashlib
import binascii
from init import *
from error import *
from Crypto.Cipher import AES
from collections import namedtuple



AES_KEY = b"R0chLi4uLi4uLi4="
BLOCK_FORMAT = struct.Struct("32s d 32s 32s 12s 12s 12s I")

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

def get_passwords():
    return {
        "POLICE": os.getenv("BCHOC_PASSWORD_POLICE"),
        "LAWYER": os.getenv("BCHOC_PASSWORD_LAWYER"),
        "ANALYST": os.getenv("BCHOC_PASSWORD_ANALYST"),
        "EXECUTIVE": os.getenv("BCHOC_PASSWORD_EXECUTIVE"),
        "CREATOR": os.getenv("BCHOC_PASSWORD_CREATOR")
    }

def verify_user(input_pass):
    passwords = get_passwords()
    return input_pass in passwords.values()

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_data = cipher.encrypt(data.ljust(32, b'\0'))  # Pad to 32 bytes
    return binascii.hexlify(encrypted_data)

def validate(blockchain): #Temporary use the actual validate function once its implemented; will fail tests that require validating the blockchain
    return True

def add_block(case_id, item_ids, creator, password, file_path):
    
    if not verify_user(password): #password verification throw error if false
        print('Invalid Password')
        invalid_password()

    try:
        case_uuid = uuid.UUID(case_id)
    except ValueError:
        print('Invalid case_id')
        generic_error()
    
    encrypted_case_id = encrypt_data(case_uuid.bytes, AES_KEY)

    encrypted_item_ids = []
    for item_id in item_ids:
        try:
            item_id_bytes = struct.pack('I', item_id)
        except struct.error:
            print('Invalid item_id')
            generic_error()

        encrypted_item_ids.append(encrypt_data(item_id_bytes, AES_KEY))

    
    if not os.path.exists(file_path):
        init(file_path)
    
    
    if not validate(file_path):
        print('Invalid Blockchain file')
        invalid_blockchain()

    f = open(file_path, 'rb')
    
    block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id item_id state creator owner data_length')
    block_data = namedtuple('Block_Data', 'data')

    prev_hash = ''
    prev_ids = []

    while True:

        try:
            head = f.read(BLOCK_FORMAT.size)
            curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
            prev_ids.append(curr_head.item_id)
            DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data = f.read(curr_head.data_length)
            curr_data = data._make(DATA_FORMAT.unpack(data))

            prev_hash = hashlib.sha256(head+data).digest()
        except:
            return False
        
    



''' 

def add_block(case_id, item_ids, creator, password, file_path):
    if not verify_user(password):
        print('Invalid Password')
        invalid_password()

    # Ensure file exists and create genesis block if it doesn't
    try:
        f = open(file_path, 'rb')
        f.close()
    except FileNotFoundError:
        genesis = create_genesis_block(GENESIS_BLOCK)
        with open(file_path, 'wb') as f:
            f.write(genesis)

    f = open(file_path, 'rb')
    block_head_tuple = namedtuple('Block_Head', 'prev_hash timestamp case_id item_id state creator owner data_length')
    block_data_tuple = namedtuple('Block_Data', 'data')

    prev_hash = b''
    prev_ids = set()  # Use a set for faster lookup of previous IDs

    while True:
        try:
            head_content = f.read(BLOCK_FORMAT.size)
            if not head_content:
                break
            curr_head = block_head_tuple._make(BLOCK_FORMAT.unpack(head_content))
            prev_ids.add(curr_head.item_id)  
            BLOCK_DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
            data_content = f.read(curr_head.data_length)
            curr_data = block_data_tuple._make(BLOCK_DATA_FORMAT.unpack(data_content))
            prev_hash = hashlib.sha256(head_content + data_content).digest()
        except struct.error:
            break

    f.close()

    for item in item_ids:
        # Ensure item_id is an integer
        # Pack item_id as a 4-byte integer and pad it to 32 bytes
        item_id_bytes = struct.pack('I', item).ljust(32, b'\x00')

        # Check if the padded item_id already exists in prev_ids
        if item_id_bytes in prev_ids:
            print("evidence Id duplicate detected")
            duplicate_evidence()
            return False



        now = datetime.now()
        timestamp = datetime.timestamp(now)
        case_id_bytes = uuid.UUID(case_id).bytes
        head_values = (prev_hash, timestamp, case_id_bytes, item_id_bytes, str.encode('CHECKEDIN'), str.encode(creator), str.encode(''), 0)
        data = b''
        BLOCK_DATA_FORMAT = struct.Struct('0s')
        packed_head = BLOCK_FORMAT.pack(*head_values)
        packed_data = BLOCK_DATA_FORMAT.pack(data)
        curr_head = block_head_tuple._make(BLOCK_FORMAT.unpack(packed_head))
        curr_data = block_data_tuple._make(BLOCK_DATA_FORMAT.unpack(packed_data))

        print(f"curr head: {curr_head}")
        print(f"curr_data: {curr_data}")

        prev_hash = hashlib.sha256(packed_head + packed_data).digest()

        with open(file_path, 'ab') as f:
            f.write(packed_head)
            f.write(packed_data)

        print("Added item:", item)
        print("Status: CHECKEDIN")
        print("Time of action:", now.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z')

    return True

'''