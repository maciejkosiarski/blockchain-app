from utils.verification import Verification
from blockchain import Blockchain


class Node:
    def __init__(self):
        self.id = 'Maciej'
        # self.id = str(uuid4())
        self.blockchain: Blockchain = Blockchain(self.id)

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
            print('3: Output the blockchains blocks')
            print('4: Check transaction validity')
            print('q: Quit')

            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transaction is valid!')
                else:
                    print('There are invalid transactions')
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break
            print(30 * '-')
            print('Balance of {}:{:6.2f} coins'.format(self.id, self.blockchain.get_balance()))
        else:
            print('User left!')


if __name__ == '__main__':
    node = Node()
    node.listen_to_input()
