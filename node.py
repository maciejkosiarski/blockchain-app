from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return jsonify({
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance(),
        }), 201
    else:
        return jsonify({'message': 'Saving the keys failed.'}), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return jsonify({
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }), 201
    else:
        return jsonify({'message': 'Loading the keys failed.'}), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance is not None:
        return jsonify({'message': 'Fetched balance successfully.','funds': balance}), 200
    else:
        return jsonify({'message': 'Loading balance failed.','wallet_set_up': wallet.public_key is not None}), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        return jsonify({'message': 'No wallet set up.'}), 400

    values = request.get_json()

    if not values:
        return jsonify({'message': 'Not data found.'}),

    required_fields = ['recipient', 'amount']

    if not all(field in values for field in required_fields):
        return jsonify({'message': 'Required data is missing'}), 400

    signature = wallet.sign_transaction(wallet.public_key, values['recipient'], values['amount'])
    success = blockchain.add_transaction(values['recipient'], wallet.public_key, signature, values['amount'])

    if success:
        return jsonify({
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': signature,
            },
            'funds': blockchain.get_balance(),
        }), 201
    else:
        return jsonify({'message': 'Creating a transaction failed.'}), 500


@app.route('/main', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        return jsonify({
            'message': 'Block added successfully.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }), 201
    else:
        return jsonify({'message': 'Adding a block failed.', 'wallet_set_up': wallet.public_key is not None}), 500


@app.route('/transaction', methods=['GET'])
def get_open_transaction():
    return jsonify([tx.__dict__ for tx in blockchain.get_open_transactions()]), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__ for block in chain_snapshot]

    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]

    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        return jsonify({'message': 'No data attached'}), 400

    if 'node' not in values:
        return jsonify({'message': 'No data attached'}), 400

    node = values.get('node')
    blockchain.add_peer_node(node)
    return jsonify({'message': 'Node added successfully.', 'all_nodes': blockchain.get_peer_nodes()}), 200


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url is None:
        return jsonify({'message': 'No node found.'}), 400
    blockchain.remove_peer_node(node_url)
    return jsonify({
        'message': 'Node removed.',
        'all_nodes': blockchain.get_peer_nodes(),
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

