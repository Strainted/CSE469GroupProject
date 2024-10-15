import sys
import argparse
from blockchain import Blockchain
from block import Block 

def parse_arguments():
    parser = argparse.ArgumentParser(description="Blockchain Chain of Custody Program")

    subparsers = parser.add_subparsers(dest='command')

    # Add command
    add_parser = subparsers.add_parser('add')
    add_parser.add_argument('-c', '--case_id', required=True)
    add_parser.add_argument('-i', '--item_id', nargs='+', required=True)
    add_parser.add_argument('-g', '--creator', required=True)
    add_parser.add_argument('-p', '--password', required=True)

    # Checkout command
    checkout_parser = subparsers.add_parser('checkout')
    checkout_parser.add_argument('-i', '--item_id', required=True)
    checkout_parser.add_argument('-p', '--password', required=True)

    # Checkin command
    checkin_parser = subparsers.add_parser('checkin')
    checkin_parser.add_argument('-i', '--item_id', required=True)
    checkin_parser.add_argument('-p', '--password', required=True)

    # Show cases command
    show_cases_parser = subparsers.add_parser('show')
    show_cases_parser.add_argument('subcommand', choices=['cases', 'items', 'history'])
    show_cases_parser.add_argument('-c', '--case_id')
    show_cases_parser.add_argument('-i', '--item_id')
    show_cases_parser.add_argument('-n', '--num_entries', type=int)
    show_cases_parser.add_argument('-r', '--reverse', action='store_true')
    show_cases_parser.add_argument('-p', '--password', required=True)

    # Remove command
    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('-i', '--item_id', required=True)
    remove_parser.add_argument('-y', '--reason', required=True, choices=['DISPOSED', 'DESTROYED', 'RELEASED'])
    remove_parser.add_argument('-p', '--password', required=True)
    remove_parser.add_argument('-o', '--owner')

    # Init command
    subparsers.add_parser('init')

    # Verify command
    subparsers.add_parser('verify')

    return parser.parse_args()

def main():
    args = parse_arguments()
    blockchain = Blockchain()  # Initialize the blockchain
    
    if args.command == 'init':
        if not blockchain.blocks:  # Only call init if blocks list is empty
            blockchain.init()
            return
    elif args.command == 'add':
        case_id = args.case_id
        item_ids = [int(id) for id in args.item_id]  # Convert item_ids to integers
        creator = args.creator
        password = args.password
        blockchain.add_block(case_id, item_ids, creator, password)
        return

    elif args.command == 'checkout':
        return 

    elif args.command == 'checkin':
        return 

    elif args.command == 'show':
        if args.subcommand == 'cases':
            return
        elif args.subcommand == 'items':
            return
        elif args.subcommand == 'history':
            return
        
    elif args.command == 'remove':
        return
    
    elif args.command == 'verify':
       return

if __name__ == "__main__":
    main()
