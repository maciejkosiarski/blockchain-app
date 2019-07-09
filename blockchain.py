from functools import reduce
import json
# import pickle
# from dumper import dump

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
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

                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in
                                  [Block(block_el.index, block_el.previous_hash,
                                         [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp)
                                   for
                                   block_el in self.chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(saveable_tx))
                # data_to_save = {
                #     'chain': block_chain,
                #     'ot': open_transactions,
                # }
                # f.write(pickle.dumps(data_to_save))
        except IOError:
            print('Blockchain saving failed!')

    def proof_of_work(self) -> int:
        last_hash = hash_block(self.chain[-1])
        proof = 0
        print('Proof of work...')
        verifier = Verification()
        while not verifier.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1

        return proof

    def get_balance(self) -> float:
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.chain]
        open_tx_sender = [tx.amount for tx in self.open_transactions
                          if tx.sender == participant]
        tx_sender.append(open_tx_sender)

        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender,
                             0)

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                                 tx_recipient, 0)

        return float(amount_received - amount_sent)

    def get_last_block_chain_value(self):
        if len(self.chain) <= 0:
            return None
        return self.chain[-1]

    def add_transaction(self, recipient: str, sender: str, amount: float = 1.0):
        verifier = Verification()
        transaction = Transaction(sender, recipient, amount)
        if verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self) -> bool:
        last_block = self.chain[-1]
        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)
        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)
        block = Block(len(self.chain), hash_block(last_block), copied_transactions, self.proof_of_work())
        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
        return True

