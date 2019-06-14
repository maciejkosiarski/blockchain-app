from functools import reduce
import json
import pickle
from dumper import dump

from hash_util import hash_string_256, hash_block
from block import Block
from transaction import Transaction

MINING_REWARD = 10

block_chain = []
open_transactions = []
block_chain_source = 'blockchain.txt'
owner = 'Maciej'
participants = {'Maciej'}


def load_data():
    global block_chain
    global open_transactions
    try:
        with open(block_chain_source, mode='r') as f:
            # file_content = pickle.loads(f.read())
            file_content = f.readlines()
            # block_chain = file_content['chain']
            # open_transactions = file_content['ot']
            block_chain = json.loads(file_content[0][:-1])
            updated_blockchain = []

            for block in block_chain:
                converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in
                                block['transactions']]
                updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'],
                                      block['timestamp'])
                updated_blockchain.append(updated_block)

            block_chain = updated_blockchain
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    except (IOError, IndexError):
        genesis_block = Block(0, '', [], 100, 0)
        block_chain = [genesis_block]
        open_transactions = []
    finally:
        print('Cleanup!')


load_data()


def save_data():
    try:
        with open(block_chain_source, mode='w') as f:
            saveable_chain = [block.__dict__ for block in
                              [Block(block_el.index, block_el.previous_hash,
                                     [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp)
                               for
                               block_el in block_chain]]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions]
            f.write(json.dumps(saveable_tx))
            # data_to_save = {
            #     'chain': block_chain,
            #     'ot': open_transactions,
            # }
            # f.write(pickle.dumps(data_to_save))
    except IOError:
        print('Blockchain saving failed!')


def valid_proof(transactions: list, last_hash: str, proof) -> bool:
    guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0:2] == '00'


def proof_of_work() -> int:
    last_hash = hash_block(block_chain[-1])
    proof = 0
    print('Proof of work...')
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1

    return proof


def get_balance(participant: str) -> float:
    tx_sender = [[tx.amount for tx in block.transactions
                  if tx.sender == participant] for block in block_chain]
    open_tx_sender = [tx.amount for tx in open_transactions
                      if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    print(tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender,
                         0)

    tx_recipient = [[tx.amount for tx in block.transactions
                     if tx.recipient == participant] for block in block_chain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                             tx_recipient, 0)

    return float(amount_received - amount_sent)


def get_last_block_chain_value():
    if len(block_chain) <= 0:
        return None
    return block_chain[-1]


def verify_transaction(transaction: Transaction) -> bool:
    return get_balance(transaction.sender) >= transaction.amount


def add_transaction(recipient: str, sender: str = owner, amount: float = 1.0):
    transaction = Transaction(sender, recipient, amount)
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


def mine_block() -> bool:
    last_block = block_chain[-1]
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = Block(len(block_chain), hash_block(last_block), copied_transactions, proof_of_work())
    block_chain.append(block)
    return True


def get_transaction_value() -> tuple:
    tx_recipient = str(input('Enter the recipient of the transaction: '))
    tx_amount = float(input('Your transaction amount please: '))
    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    for block in block_chain:
        print('Outputting Block')
        dump(block)
    else:
        print(20 * '-')


def verify_chain():
    for (index, block) in enumerate(block_chain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(block_chain[index - 1]):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print('Proof of work is invalid!')
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

while waiting_for_input:
    print('Please chose')
    print('1: Add new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchains blocks')
    print('4: Output all participants')
    print('5: Check transaction validity')
    print('q: Quit')

    user_choice = get_user_choice()

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transaction is valid!')
        else:
            print('There are invalid transactions')
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
    print(30 * '-')
    print('Balance of {}:{:6.2f} coins'.format(owner, get_balance(owner)))
else:
    print('User left!')
