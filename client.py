import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back
from enigma.machine import EnigmaMachine

# init colors
init()

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]
# choose a random color for the client
client_color = random.choice(colors)

# setup machine according to specs from a daily key sheet:

machine = EnigmaMachine.from_key_sheet(
       rotors='II IV V',
       reflector='B',
       ring_settings=[1, 20, 11],
       plugboard_settings='AV BS CG DL FU HZ IN KM OW RX')


# server's IP address
# if the server is not on this machine, 
# put the private (network) IP address (e.g 192.168.1.2)
def opening_inputs():
    server_host = ""
    print("Would you like to use a default server host or enter a private IP address?")
    
    option = ""

    while option != "1" or option != "2":
        print("1: Default Server Host")
        print("2: Enter private IP address")

        option = input("")

        if option == "1":
            server_host = "127.0.0.1"
            return server_host
        elif option == "2":
            server_host = input("Enter IP address: ")
            return server_host
        else:
            print("Invalid input. Please enter a valid option.")



SERVER_HOST = opening_inputs()

SERVER_PORT = 5002        # server's port
separator_token = "<SEP>" # we will use this to separate the client name & message


# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")

# prompt the client for a name
name = input("Enter your name: ")

# set machine initial starting position
startingPosition = input("Enter the intiial starting position: ")

#machine.set_display('WXC')
machine.set_display(startingPosition)

messageKey = input("Enter the message key: ")

# decrypt the message key
msg_key = machine.process_text(messageKey)

# decrypt the cipher text with the unencrypted message key
machine.set_display(msg_key)

print("Registered. You can now start typing for messages.")

def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        splitmessage = message.split('  ')
        timestamp = splitmessage[0]
        machine.set_display(msg_key)
        decoded = machine.process_text(splitmessage[1])
        print("\n" + timestamp + " " + decoded)
       
# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)

# make the thread daemon so it ends whenever the main thread ends
t.daemon = True

# start the thread
t.start()

while True:
    # input message we want to send to the server
    to_send =  input()

    # decrypt the cipher text with the unencrypted message key
    machine.set_display(msg_key)

    plaintext = to_send
    ciphertext = machine.process_text(plaintext)
    to_send_message = ciphertext

    # a way to exit the program
    if to_send.lower() == 'q':
        break
    # add the datetime, name & the color of the sender
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    to_send = f"{client_color}[{date_now}] {name}{separator_token} {to_send_message}"
    # finally, send the message
    s.send(to_send.encode())

# close the socket
s.close()