import sys
import argparse
import os
from init import init
from add import add_block
from error import *
from checkout import *
from checkin import *
from remove import remove_item
from show import *
from verify import verify_blockchain

BLOCKCHAIN_FILE = os.getenv('BCHOC_FILE_PATH', 'blockchain.dat')

# This function was generated with assistance from ChatGPT, an AI tool developed by OpenAI.
# Reference: OpenAI. (2024). ChatGPT [Large language model]. openai.com/chatgpt
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
    show_cases_parser.add_argument('-p', '--password', required=False)

    # Remove command
    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('-i', '--item_id', required=True)
    remove_parser.add_argument('-y', '--reasonY', required=False, choices=['DISPOSED', 'DESTROYED', 'RELEASED'],
                               dest='reason')
    remove_parser.add_argument('--why', '--reasonW', required=False, choices=['DISPOSED', 'DESTROYED', 'RELEASED'],
                               dest='reason')
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
        show = Show()
        if args.subcommand == 'cases':
            show.show_cases(BLOCKCHAIN_FILE)
            return
        elif args.subcommand == 'items':
            if not args.case_id:
                print("Missing case_id for show items")
                sys.exit(1)
            show = Show()
            show.show_items(BLOCKCHAIN_FILE, args.case_id)
            return
        elif args.subcommand == 'history':
            return

    elif args.command == 'remove':
        item_id = int(args.item_id)
        password = args.password
        if args.reason is None:
            print("Error: One of the arguments '-y' or '--why' must be provided.")
            sys.exit(1)
        reason = args.reason
        owner = args.owner if reason == 'RELEASED' else None
        remove_item(item_id, reason, password, owner, BLOCKCHAIN_FILE)
        return

    elif args.command == 'verify':
        verify_blockchain(BLOCKCHAIN_FILE)
        return


if __name__ == "__main__":
    main()
