from hashlib import sha256
import json

from block import Block


def hash_string_256(string: bytes) -> str:
    return sha256(string).hexdigest()


def hash_block(block: Block) -> str:
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
