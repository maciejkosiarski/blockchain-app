from functools import reduce
import json
# import pickle
# from dumper import dump

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

MINING_REWARD = 10

block_chain = []
open_transactions = []
block_chain_source = 'blockchain.txt'
owner = 'Maciej'


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


def proof_of_work() -> int:
    last_hash = hash_block(block_chain[-1])
    proof = 0
    print('Proof of work...')
    verifier = Verification()
    while not verifier.valid_proof(open_transactions, last_hash, proof):
        proof += 1

    return proof


def get_balance(participant: str) -> float:
    tx_sender = [[tx.amount for tx in block.transactions
                  if tx.sender == participant] for block in block_chain]
    open_tx_sender = [tx.amount for tx in open_transactions
                      if tx.sender == participant]
    tx_sender.append(open_tx_sender)

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


def add_transaction(recipient: str, sender: str = owner, amount: float = 1.0):
    verifier = Verification()
    transaction = Transaction(sender, recipient, amount)
    if verifier.verify_transaction(transaction, get_balance):
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

