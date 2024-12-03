# TODO state field is adding an extra null byte when being packed 
# TODO test cases with multiple item_ids is not returning the proper values 

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
from datetime import datetime



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

GENESIS_HASH = hashlib.sha256(create_block(GENESIS_BLOCK)).digest()

def create_block(block_data):
    
    DATA_FORMAT = struct.Struct(str(block_data['d_length']) + 's')

    return BLOCK_FORMAT.pack(
                       block_data['prev_hash'],
                       block_data['timestamp'],
                       block_data['case_id'],
                       block_data['evidence_id'],
                       block_data['state'],
                       block_data['creator'],
                       block_data['owner'],
                       block_data['d_length'],
                    ) + DATA_FORMAT.pack(block_data['data'])


def get_passwords():
    passwords = {
        "POLICE": os.getenv("BCHOC_PASSWORD_POLICE"),
        "LAWYER": os.getenv("BCHOC_PASSWORD_LAWYER"),
        "ANALYST": os.getenv("BCHOC_PASSWORD_ANALYST"),
        "EXECUTIVE": os.getenv("BCHOC_PASSWORD_EXECUTIVE"),
        "CREATOR": os.getenv("BCHOC_PASSWORD_CREATOR")
    }
    return passwords


def verify_user(input_pass):
    passwords = get_passwords()
    if input_pass != passwords["CREATOR"]:
        print("Invalid Password")
        invalid_password()  
    return True

def encrypt_data(data, key):
    # Ensure the data is a multiple of 16 bytes for AES encryption
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = data + b'\0' * (16 - len(data) % 16)
    encrypted_data = cipher.encrypt(padded_data)
    return binascii.hexlify(encrypted_data)


def decrypt_data(encrypted_data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(binascii.unhexlify(encrypted_data))
    return decrypted_data.rstrip(b'\0')


def validate(blockchain): #Temporary use the actual validate function once its implemented; will fail tests that require validating the blockchain
    return True

def add_block(case_id, item_ids, creator, password, file_path):
    
    verify_user(password)
        
    try:
        case_uuid = uuid.UUID(case_id)
    except ValueError:
        print('Invalid case_id')
        generic_error()
    
    encrypted_case_id = encrypt_data(case_uuid.bytes, AES_KEY)

    encrypted_item_ids = []
    for item_id in item_ids:
        try:
            item_id_bytes = item_id.to_bytes(16, byteorder='big')  # Convert to 16 bytes
        except OverflowError:
            print('Invalid item_id')
            exit_0()


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
        head = f.read(BLOCK_FORMAT.size)
        if not head:
            break
        curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
        prev_ids.append(curr_head.item_id)
        DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
        data = f.read(curr_head.data_length)
        curr_data = block_data._make(DATA_FORMAT.unpack(data))
        prev_hash = hashlib.sha256(head+data).digest()
        if prev_hash == GENESIS_HASH:
            prev_hash = b'0'
        
    f.close()
    
    new_blocks = []
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    for encrypted_item_id in encrypted_item_ids:
            decrypted_item_id = decrypt_data(encrypted_item_id, AES_KEY)
            if decrypted_item_id in [decrypt_data(prev_id, AES_KEY) for prev_id in prev_ids]:
                print('Duplicate Evidence Detected')
                duplicate_evidence()

            block_data = {
                'prev_hash': prev_hash,
                'timestamp': timestamp,
                'case_id': encrypted_case_id,
                'evidence_id': encrypted_item_id,
                'state': b'CHECKEDIN',
                'creator': creator.encode(),
                'owner': b'\0' * 12,
                'd_length': 0, 
                'data': b''
            }
            
            new_block = create_block(block_data)
            new_blocks.append(new_block)
            prev_hash = hashlib.sha256(new_block).digest()

    with open(file_path, 'ab') as f:
        for block in new_blocks:
            f.write(block)
            for item_id in item_ids:
                print(f"Added item: {item_id}")
                print("Status: CHECKEDIN")
                print(f"Time of action: {datetime.timestamp(datetime.now())}Z") 

    return True