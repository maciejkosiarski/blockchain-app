"""Provides verification helper methods"""

from transaction import Transaction
from utils.hash_util import hash_string_256, hash_block


class Verification:
    @staticmethod
    def valid_proof(transactions: list, last_hash: str, proof) -> bool:
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'

    @classmethod
    def verify_chain(cls, block_chain):
        for (index, block) in enumerate(block_chain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(block_chain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid!')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction: Transaction, get_balance) -> bool:
        return get_balance() >= transaction.amount

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        return all([cls.verify_transaction(tx, get_balance) for tx in open_transactions])
