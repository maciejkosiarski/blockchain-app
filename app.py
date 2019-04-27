
block_chain = []


def get_last_block_chain_value():
    if len(block_chain) <= 0:
        return None
    return block_chain[-1]


def add_transaction(transaction_amount, last_transaction=[1]):
    if last_transaction is None:
        last_transaction = [1]
    block_chain.append([last_transaction, transaction_amount])


def get_transaction_value():
    user_input = float(input('Your transaction amount please: '))
    return user_input


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
    is_valid = True

    for block_index in range(len(block_chain)):
        if block_index == 0:
            continue
        if block_chain[block_index][0] != block_chain[block_index - 1]:
            is_valid = False
            break

    return is_valid


waiting_for_input = True


while waiting_for_input:
    print('Please chose')
    print('1: Add new transaction value')
    print('2: Output the blockchains blocks')
    print('h: Manipulate the chain')
    print('q: Quit')

    user_choice = get_user_choice()

    if user_choice == '1':
        add_transaction(get_transaction_value(), get_last_block_chain_value())
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == 'h':
        if len(block_chain) >= 1:
            block_chain[0] = 2
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
else:
    print('User left!')
