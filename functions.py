import _thread
import time
import random


def do_now(t_name, num):
    time.sleep(random.randint(1, 10))
    print('Hello I am thread {}'.format(t_name))
    print('I have number {}'.format(num))


_thread.start_new_thread(do_now, ('thread ONE', 1))
_thread.start_new_thread(do_now, ('thread TWO', 2))
_thread.start_new_thread(do_now, ('thread THREE', 3))
_thread.start_new_thread(do_now, ('thread FOUR', 4))
_thread.start_new_thread(do_now, ('thread FIVE', 5))
_thread.start_new_thread(do_now, ('thread SIX', 6))
_thread.start_new_thread(do_now, ('thread SEVEN', 7))
_thread.start_new_thread(do_now, ('thread EIGHT', 8))
_thread.start_new_thread(do_now, ('thread NINE', 9))
_thread.start_new_thread(do_now, ('thread TEN', 10))

while 1:
    pass


def unlimited_arguments(*args):
    for argument in args:
        print(argument)


def return_text(text: str) -> str:
    return text


name: str = 'Maciej'
name = 1

print()

# print_text('hello')
# print_text(1)
# print_text(1.0)
# print_text([1, 2, 'Hello'])
# print_text({'name': 'Maciej'})

# unlimited_arguments(1, 2, 3, 4)

