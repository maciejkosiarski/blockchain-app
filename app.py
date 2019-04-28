from functools import reduce
from hashlib import sha256
import json
from collections import OrderedDict

MINING_REWARD = 10

genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100,
}
block_chain = [genesis_block]
open_transactions = []
owner = 'Maciej'
participants = {'Maciej'}


def hash_block(block) -> str:
    return sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()


def valid_proof(transactions: list, last_has: str, proof) -> bool:
    guess = (str(transactions) + str(last_has) + str(proof)).encode()
    guess_hash = sha256(guess).hexdigest()
    return guess_hash[0:2] == '00'


def proof_of_work() -> int:
    last_hash = hash_block(block_chain[-1])
    proof = 0
    print('Proof of work...')
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1

    return proof


def get_balance(participant: str) -> float:
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in block_chain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)

    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in
                    block_chain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

    return float(amount_received - amount_sent)


def get_last_block_chain_value():
    if len(block_chain) <= 0:
        return None
    return block_chain[-1]


def verify_transaction(transaction: dict) -> bool:
    return get_balance(transaction['sender']) >= transaction['amount']


def add_transaction(recipient: str, sender: str = owner, amount: float = 1.0):
    transaction = OrderedDict([
        ('sender', sender),
        ('recipient', recipient),
        ('amount', amount),
    ])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block() -> bool:
    last_block = block_chain[-1]
    reward_transaction = OrderedDict([
        ('sender', 'MINING'),
        ('recipient', owner),
        ('amount',  MINING_REWARD),
    ])
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block_chain.append({
        'previous_hash': hash_block(last_block),
        'index': len(block_chain),
        'transactions': copied_transactions,
        'proof': proof_of_work(),
    })
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
        print(block)
    else:
        print(20 * '-')


def verify_chain():
    for (index, block) in enumerate(block_chain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(block_chain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
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
    print('h: Manipulate the chain')
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
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transaction is valid!')
        else:
            print('There are invalid transactions')
    elif user_choice == 'h':
        if len(block_chain) >= 1:
            block_chain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Chris', 'recipient': 'Maciej', 'amount': 100.0}],
            }
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
