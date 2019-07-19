from utils.verification import Verification
from blockchain import Blockchain
from wallet import Wallet


class Node:
    def __init__(self):
        self.wallet: Wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self) -> tuple:
        return str(input('Enter the recipient of the transaction: ')), float(input('Your transaction amount please: '))

    def get_user_choice(self):
        return input('Your choice: ')

    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
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
            print('3: Output the blockchain blocks')
            print('4: Check transaction validity')
            print('5: Create new wallet')
            print('6: Load wallet')
            print('7: Save keys')
            print('q: Quit')

            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining failed. Got no wallet?')
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                open_transactions = self.blockchain.get_open_transactions()
                if Verification.verify_transactions(open_transactions, self.blockchain.get_balance):
                    print('All transaction is valid!')
                else:
                    print('There are invalid transactions')
            elif user_choice == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break
            print(30 * '-')
            print('Balance of {}:{:6.2f} coins'.format(self.wallet.public_key, self.blockchain.get_balance()))
        else:
            print('User left!')


if __name__ == '__main__':
    node = Node()
    node.listen_to_input()
