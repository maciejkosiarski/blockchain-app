from functools import reduce
import json
# import pickle
# from dumper import dump
import requests

from block import Block
from transaction import Transaction
from wallet import Wallet

from utils.hash_util import hash_block
from utils.verification import Verification

MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.load_data()

    @property
    def chain(self) -> list:
        return self.__chain

    @chain.setter
    def chain(self, value):
        self.__chain = value

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                # file_content = pickle.loads(f.read())
                file_content = f.readlines()
                # block_chain = file_content['chain']
                # open_transactions = file_content['ot']
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []

                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in
                                    block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'],
                                          block['timestamp'])
                    updated_blockchain.append(updated_block)

                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                self.__peer_nodes = set(json.loads(file_content[2]))
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                saveable_chain = [block.__dict__ for block in
                                  [Block(block_el.index, block_el.previous_hash,
                                         [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp)
                                   for
                                   block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
                # data_to_save = {
                #     'chain': block_chain,
                #     'ot': open_transactions,
                # }
                # f.write(pickle.dumps(data_to_save))
        except IOError:
            print('Blockchain saving failed!')

    def proof_of_work(self) -> int:
        last_hash = hash_block(self.__chain[-1])
        proof = 0
        print('Proof of work...')
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1

        return proof

    def get_balance(self, sender=None) -> float:
        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender

        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions
                          if tx.sender == participant]
        tx_sender.append(open_tx_sender)

        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender,
                             0)

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                                 tx_recipient, 0)

        return float(amount_received - amount_sent)

    def get_last_block_chain_value(self):
        if len(self.__chain) <= 0:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient: str, sender: str, signature: str, amount: float = 1.0, is_receiving=False) -> bool:
        if self.public_key is None:
            return False

        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender,'recipient': recipient,'amount': amount,'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        if self.public_key is None:
            return None

        last_block = self.__chain[-1]
        reward_transaction = Transaction('MINING', self.public_key, '', MINING_REWARD)
        copied_transactions = self.__open_transactions[:]

        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hash_block(last_block), copied_transactions, self.proof_of_work())

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block

    def add_peer_node(self, node_url):
        self.__peer_nodes.add(node_url)
        self.save_data()

    def remove_peer_node(self, node_url):
        self.__peer_nodes.discard(node_url)
        self.save_data()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)
