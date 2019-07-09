class Node:
    def __init__(self):
        self.blockchain = []

    def get_transaction_value(self) -> tuple:
        return str(input('Enter the recipient of the transaction: ')), float(input('Your transaction amount please: '))

    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    def print_blockchain_elements(self):
        for block in self.blockchain:
            print('Outputting Block')
            print(block)
        else:
            print(20 * '-')

    def listen_to_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print('Please chose')
            print('1: Add new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchains blocks')
            print('4: Check transaction validity')
            print('q: Quit')

            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_data = self.get_transaction_value()
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
                self.print_blockchain_elements()
            elif user_choice == '4':
                verifier = Verification()
                if verifier.verify_transactions(open_transactions, get_balance):
                    print('All transaction is valid!')
                else:
                    print('There are invalid transactions')
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            verifier = Verification()
            if not verifier.verify_chain(block_chain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break
            print(30 * '-')
            print('Balance of {}:{:6.2f} coins'.format(owner, get_balance(owner)))
        else:
            print('User left!')
