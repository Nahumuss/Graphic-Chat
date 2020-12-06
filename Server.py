import socket, pickle
import select

from Classes.Message import *
from Classes.CommandMessage import *
from Classes.TwoWayDict import TwoWayDict
from threading import Thread
import json

name_socket = TwoWayDict()

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(5)


open_client_sockets = []

messages_to_send = []

admins = []

muted = []

def is_admin(username):
    with open('users.json') as json_file:
        users = json.load(json_file)
        for u in users:
            if u['username'] == username and u['admin']:
                return True
    return False

def is_muted(username):
    with open('users.json') as json_file:
        users = json.load(json_file)
        for u in users:
            if u['username'] == username and u['muted']:
                return True
    return False

def set_muted(username, muted):
    with open('users.json', 'r+') as json_file:
        users = json.load(json_file)
        for u in users:
            if u['username'] == username:
                u['muted'] = muted
        json_file.seek(0)
        json_file.truncate()
        json.dump(users, json_file, indent=4)
        json_file.close()

def set_admin(username, admin):
    with open('users.json', 'r+') as json_file:
        users = json.load(json_file)
        for u in users:
            if u['username'] == username:
                u['admin'] = admin
        json_file.seek(0)
        json_file.truncate()
        json.dump(users, json_file, indent=4)
        json_file.close()

def check_login(username, password):
    with open('users.json') as json_file:
        users = json.load(json_file)
        for u in users:
            if (u['username'] == username and u['password'] == password) and username not in name_socket:
                return True
    return False

def register(username, password):
    with open('users.json', 'r+') as json_file:
        users = json.load(json_file)
        for u in users:
            if u['username'] == username:
                return False
        user = {'username': username, 'password': password, 'admin': False, 'muted': False}
        users.append(user)
        json_file.seek(0)
        json.dump(users, json_file, indent=4)
    return True


def send_messages():
    for message in messages_to_send:
        if type(message) is CommandMessage:
            for client in message.destinations:
                try:
                    socket = name_socket[client]
                    socket.send(str(message).encode())
                except:
                    pass
        elif type(message) is BroadcastMessage or Message:
            for socket in open_client_sockets:
                socket.send(str(message).encode())
        messages_to_send.remove(message)

def handle_message(message, current_socket):
    print('To ' + str(message.destinations) + str(message))
    if message.command == commands['login']:
        if check_login(message.source, message.data):
            current_socket.send('s'.encode())
            name_socket[current_socket] = message.source
            messages_to_send.append(BroadcastMessage(message.source + ' Has joined the chat!'))
        else:
            current_socket.send('e'.encode()) 
    if message.command == commands['disconnect']:
        open_client_sockets.remove(current_socket)
        del name_socket[current_socket]
        messages_to_send.append(BroadcastMessage(message.source + ' Has left the chat!'))
    if message.command == commands['register']:
        if register(message.source, message.data):
            current_socket.send('succ'.encode())
            name_socket[current_socket] = message.source
        else:
            current_socket.send('err'.encode()) 
    if message.command == commands['mute']:
        for destination in message.destinations:
            try:
                set_muted(destination, True)
            except:
                print('Could not mute user ' + destination)
    if message.command == commands['unmute']:
        for destination in message.destinations:
            try:
                set_muted(destination, False)
            except:
                print('Could not unmute ' + destination)
    if message.command == commands['kick']:
        for destination in message.destinations:
            try:
                open_client_sockets.remove(name_socket[destination])
                name_socket[destination].close()
                del name_socket[destination]
            except:
                print('Could not kick ' + destination)
    if message.command == commands['promote']:
        for destination in message.destinations:
            try:
                set_admin(destination, True)
            except:
                print('Could not promote ' + destination)
    if message.command == commands['demote']:
        for destination in message.destinations:
            try:
                set_admin(destination, False)
            except:
                print('Could not demote ' + destination)

def handle_commands():
    while True:
        raw_message = input()
        message = string_to_command(raw_message, 'Server')
        handle_message(message, None)
        messages_to_send.append(message)




handler = Thread(target=handle_commands)
handler.start()
while(True):
    rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            open_client_sockets.append(new_socket)
        else:
            message = pickle.loads(current_socket.recv(1024))
            if current_socket in name_socket:
                muted = is_muted(name_socket[current_socket])
                admin = is_admin(name_socket[current_socket])
            else:
                muted = False
                admin = False
            is_able_to_send = type(message) == CommandMessage and (admin or message.command == commands['login'] or message.command == commands['register'] or message.command == commands['whisper'] or message.command == commands['disconnect'])
            if is_able_to_send:
                handle_message(message, current_socket)
            if ((type(message) == Message and not muted) or (is_able_to_send and (message.command != commands['whisper'] or not muted))):
                messages_to_send.append(message)
    send_messages()
