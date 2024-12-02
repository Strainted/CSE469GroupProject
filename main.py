import sys
import argparse
import os
from init import init
from add import add_block
from error import *
from checkout import *
from checkin import *

BLOCKCHAIN_FILE = os.getenv('BCHOC_FILE_PATH', 'blockchain.dat')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Blockchain Chain of Custody Program")

    subparsers = parser.add_subparsers(dest='command')

    # Add command
    add_parser = subparsers.add_parser('add')
    add_parser.add_argument('-c', '--case_id', required=True)
    add_parser.add_argument('-i', '--item_id', action='append', required=True)
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
    
    if args.command == 'init':
        init(BLOCKCHAIN_FILE)
        return
        
    elif args.command == 'add':
        case_id = args.case_id
        item_ids = [int(id) for id in args.item_id] 
        creator = args.creator
        password = args.password
        add_block(case_id, item_ids, creator, password, BLOCKCHAIN_FILE)
        return

    elif args.command == 'checkout':
        item_id = int(args.item_id)
        password = args.password
        check_out(item_id, password, BLOCKCHAIN_FILE)
        return 

    elif args.command == 'checkin':
        item_id = int(args.item_id)
        password = args.password
        check_in(item_id, password, BLOCKCHAIN_FILE)
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
        

        return
    
    elif args.command == 'verify':
       return

if __name__ == "__main__":
    main()
