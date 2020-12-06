import sys
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtCore import QRect, pyqtSlot, Qt
import ctypes
from Classes.ScrollableLabel import ScrollLabel

from datetime import datetime
import socket
import pickle

from Classes.Message import *
from Classes.CommandMessage import *
from Classes.Message import *

from threading import Thread

user32 = ctypes.windll.user32

client_socket = socket.socket()
client_socket.connect(('127.0.0.1', 8000))

geometry = QRect(500, 500, 200, 200)

class ChatWindow(QWidget):

    def __init__(self, username):
        super().__init__()
        self.chat_string = 'The Beginning \n'
        self.username = username
        self.title = 'Chat - ' + self.username
        self.main_layout = QVBoxLayout()
        self.type_layout = QHBoxLayout()
        self.chat_layout = QVBoxLayout()
        self.initUI()
        self.print_messages = Thread(target=self.wait_for_messages)
        self.print_messages.start()

    def initUI(self):

        self.setGeometry(geometry)
        self.setWindowTitle(self.title)

        self.setWindowIcon(QIcon('Icons/app icon.png'))

        self.chat_text = ScrollLabel(self)
        self.chat_text.setText(self.chat_string)

        # Create textbox
        self.typebox = QLineEdit(self)
        self.typebox.setPlaceholderText('Enter Message')
        # Create a button in the window
        self.button = QPushButton('Send Message', self)

        # Creates the window layout
        self.type_layout.addWidget(self.typebox, alignment=Qt.AlignBottom)
        self.type_layout.addWidget(self.button, alignment=Qt.AlignBottom)

        self.chat_layout.addWidget(self.chat_text)
        self.main_layout.addLayout(self.chat_layout)
        self.main_layout.addLayout(self.type_layout)

        self.setLayout(self.main_layout)

        # Connect button to function on_click
        self.button.clicked.connect(self.on_click)

        self.show()

    def closeEvent(self, a0: QCloseEvent):
        timestemp = datetime.now()
        time = f'{timestemp.hour}:{timestemp.minute}'
        client_socket.send(pickle.dumps(CommandMessage(time, self.username, [], "", commands["disconnect"])))
        client_socket.close()
        sys.exit()
    
    @pyqtSlot()
    def on_click(self):
        try:
            raw_message = str(self.typebox.text())
            if raw_message:
                timestemp = datetime.now()
                time = f'{timestemp.hour}:{timestemp.minute}'
                message = None
                if raw_message.startswith('/'):
                    message = string_to_command(raw_message[1:], self.username)
                else:
                    message = Message(time, self.username, raw_message)
                client_socket.send(pickle.dumps(message))
        finally:
            self.typebox.setText('')

    def wait_for_messages(self):
        while True:
            message = client_socket.recv(1024).decode()
            self.chat_string += message + '\n'
            if 'kicked' in message:
                closeEvent()
            self.chat_text.setText(self.chat_string)


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Login'
        self.icon = 'icon.png'
        self.main_layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        self.setGeometry(geometry)

        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('Icons/app icon.png'))

        # Creates username's textbox
        self.namebox = QLineEdit(self)
        self.namebox.setPlaceholderText('Enter username')

        # Creates password's textbox
        self.passbox = QLineEdit(self)
        self.passbox.setPlaceholderText('Enter Password')
        self.passbox.setEchoMode(QLineEdit.Password)

        self.errormsg = QLabel(self)
        self.errormsg.setText('')
 
        # Create a button in the window
        self.log_button = QPushButton('Log In', self)

        self.reg_button = QPushButton('Register Instead', self)

        # Creates the window layout
        self.main_layout.addWidget(self.namebox)
        self.main_layout.addWidget(self.passbox)
        self.main_layout.addWidget(self.errormsg)
        self.main_layout.addWidget(self.log_button)
        self.main_layout.addWidget(self.reg_button)

        self.setLayout(self.main_layout)

        # Connect button to function on_click
        self.log_button.clicked.connect(self.on_click_login)
        self.reg_button.clicked.connect(self.switch_register)

        self.show()

    @pyqtSlot()
    def on_click_login(self):
        self.username = self.namebox.text()
        self.password = self.passbox.text()
        self.login()

    def switch_register(self):
        global geometry
        geometry = self.geometry()
        self.register_page = Register()
        self.register_page.show()
        self.close()

    def login(self):
        timestemp = datetime.now()
        time = f'{timestemp.hour}:{timestemp.minute}'
        client_socket.send(pickle.dumps(CommandMessage(time, self.username, [], self.password, commands['login'])))
        while True:
            message = client_socket.recv(1024).decode()
            if message == 's' or message == 'e':
                if message == 's':
                    global geometry
                    geometry = self.geometry()
                    self.chat = ChatWindow(self.username)
                    self.chat.show()
                    self.close()
                if message == 'e':
                    self.errormsg.setText('Incorrect username / Password')
                break

class Register(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Register'
        self.icon = 'icon.png'
        self.main_layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        self.setGeometry(geometry)

        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('Icons/app icon.png'))

        # Creates username's textbox
        self.namebox = QLineEdit(self)
        self.namebox.setPlaceholderText('Enter username')

        # Creates password's textbox
        self.passbox = QLineEdit(self)
        self.passbox.setPlaceholderText('Enter Password')
        self.passbox.setEchoMode(QLineEdit.Password)

        self.errormsg = QLabel(self)
        self.errormsg.setText('')

        # Create a button in the window
        self.reg_button = QPushButton('Register', self)

        self.log_button = QPushButton('Login Instead', self)

        # Creates the window layout
        self.main_layout.addWidget(self.namebox)
        self.main_layout.addWidget(self.passbox)
        self.main_layout.addWidget(self.errormsg)
        self.main_layout.addWidget(self.reg_button)
        self.main_layout.addWidget(self.log_button)

        self.setLayout(self.main_layout)

        # Connect button to function on_click
        self.log_button.clicked.connect(self.switch_login)
        self.reg_button.clicked.connect(self.on_click_register)

        self.show()

    @pyqtSlot()
    def on_click_register(self):
        self.username = self.namebox.text()
        self.password = self.passbox.text()
        self.register()

    @pyqtSlot()
    def switch_login(self):
        global geometry
        geometry = self.geometry()
        self.login_page = Login()
        self.login_page.show()
        self.close() 

    def register(self):
        timestemp = datetime.now()
        client_socket.send(pickle.dumps(CommandMessage(
            timestemp, self.username, [], self.password, commands['register'])))
        message = client_socket.recv(1024).decode()
        if message == 'succ':
            global geometry
            geometry = self.geometry()
            self.chat = ChatWindow(self.username)
            self.chat.show()
            self.close()
        if message == 'err':
            self.errormsg.setText('Could not register with these values')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Login()
    sys.exit(app.exec_())
