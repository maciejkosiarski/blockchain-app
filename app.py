MINING_REWARD = 10

genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
}
block_chain = [genesis_block]
open_transactions = []
owner = 'Maciej'
participants = {'Maciej'}


def hash_block(block) -> str:
    return '-'.join([str(block[key]) for key in block])


def get_balance(participant: str) -> float:
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in block_chain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = 0
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += tx[0]

    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in
                    block_chain]
    amount_received = 0
    for tx in tx_recipient:
        if len(tx) > 0:
            amount_received += tx[0]

    return float(amount_received - amount_sent)


def get_last_block_chain_value():
    if len(block_chain) <= 0:
        return None
    return block_chain[-1]


def verify_transaction(transaction: dict) -> bool:
    return get_balance(transaction['sender']) >= transaction['amount']


def add_transaction(recipient: str, sender: str = owner, amount: float = 1.0):
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount,
    }
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block() -> bool:
    last_block = block_chain[-1]
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    open_transactions.append(reward_transaction)
    block_chain.append({
        'previous_hash': hash_block(last_block),
        'index': len(block_chain),
        'transactions': open_transactions,
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
    return True


waiting_for_input = True

while waiting_for_input:
    print('Please chose')
    print('1: Add new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchains blocks')
    print('4: Output all participants')
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
    print('Balance for Maciej: ' + str(get_balance('Maciej')) + ' coins')
else:
    print('User left!')
