import os
import struct
import binascii
from collections import namedtuple
from Crypto.Cipher import AES
from datetime import datetime
import uuid
from add import BLOCK_FORMAT, decrypt_data, AES_KEY

class Show:
    def __init__(self):
        """
        Initialize the Show class with three empty lists:
        - cases: Stores all the cases.
        - history: Keeps track of all actions performed.
        - items: Holds the list of items.
        """
        self.cases = []   # List to store cases
        self.history = []  # List to store the history of actions
        self.items = []    # List to store items

    def add_case(self, case):
        """
        Adds a new case to the cases list and logs the action in history.
        
        Parameters:
        - case: The case to be added (can be any data type like string, dictionary, etc.)
        """
        self.cases.append(case)  # Add the case to the list
        self.history.append(f"Added case: {case}")  # Record the action in history
    
    def add_item(self, item):
        """
        Adds a new item to the items list and logs the action in history.
        
        Parameters:
        - item: The item to be added (can be any data type like string, dictionary, etc.)
        """
        self.items.append(item)  # Add the item to the list
        self.history.append(f"Added item: {item}")  # Record the action in history

    def show_case(self):
        """
        Displays all the cases that have been added to the 'cases' list.
        
        If there are no cases, it will notify the user that no cases are available.
        """
        if self.cases:
            print("Displaying all cases:")
            for case in self.cases:
                print(f"- {case}")  # Print each case
        else:
            print("No cases to display.")  # Inform if no cases exist

    def show_history(self):
        """
        Displays the entire history of actions logged in the 'history' list.
        
        If the history is empty, it will inform the user that no actions have been recorded.
        """
        if self.history:
            print("History of actions:")
            for event in self.history:
                print(f"- {event}")  # Print each action event in history
        else:
            print("No history to display.")  # Inform if history is empty

    def show_items(self):
        """
        Displays all items that have been added to the 'items' list.
        
        If there are no items, it will notify the user that no items are available.
        """
        if self.items:
            print("Displaying items:")
            for item in self.items:
                print(f"- {item}")  # Print each item
        else:
            print("No items to display.")  # Inform if no items exist

    def show_cases(self, file_path):
        """
        Shows the cases in a blockchain file by reading and processing the blockchain's block structure.
        
        Parameters:
        - file_path: The path to the blockchain file.
        """
        firstBlock = True
        if not os.path.exists(file_path):
            print("Blockchain file does not exist.")
            return

        with open(file_path, 'rb') as f:
            block_head = namedtuple('Block_Head', 'prev_hash timestamp case_id evidence_id state creator owner data_length')
            block_data = namedtuple('Block_Data', 'data')

            prev_cases = set()
            while True:
                if firstBlock:
                    firstBlock = False
                    continue

                head = f.read(BLOCK_FORMAT.size)
                if not head:
                    break
                curr_head = block_head._make(BLOCK_FORMAT.unpack(head))
                
                DATA_FORMAT = struct.Struct(str(curr_head.data_length) + 's')
                data = f.read(curr_head.data_length)
                curr_data = block_data._make(DATA_FORMAT.unpack(data))
                case_id = decrypt_data(curr_head.case_id, AES_KEY).hex()

                if len(case_id) == 32:
                    case_id = str(uuid.UUID(case_id))
                else:
                    print(f"Invalid case_id: {case_id}")
                    continue

                evidence_id = decrypt_data(curr_head.evidence_id, AES_KEY).hex()
                timestamp = datetime.fromtimestamp(curr_head.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                state = curr_head.state.decode().rstrip('\0')
                creator = curr_head.creator.decode().rstrip('\0')

                # Add case ID to set of previous cases
                prev_cases.add(case_id)

        for case in prev_cases:
            print(f"Case: {case:<40}\n")

        return True

# Example usage of the Show class:

# Create an instance of Show

