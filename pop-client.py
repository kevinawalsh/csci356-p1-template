#!/usr/bin/python3

# Author: K. Walsh <kwalsh@cs.holycross.edu>
# Date: 20 August 2020
#
# A simple POP3 client from scratch in Python. Run it like this:
#   ./pop3-client.py whitehouse.kwalsh.org 110
#
# It will connect to whitehouse.kwalsh.org on port 110, the standard POP3 port,
# then allow the user to send and receive data.
# - To send data, type "send" followed by something, then hit enter. A standard
#   POP3 line ending "\r\n" will be sent automatically as well.
# - To receive data, type "recv" then hit enter.
#
# Note: This code is not "pythonic" at all; there are more concise ways to write
# this code by using python features like dicts and string interpolation. We
# also avoid use of any modules except for a few basic ones.

import socket    # for socket stuff
import sys       # for sys.argv
import traceback # for printing exceptions

# Global configuration variables, with default values
server_host = None
server_port = None

class SocketError:
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return "Socket Error: " + msg

ERR_SOCKET_WAS_CLOSED = SocketError("Connection Closed")
ERR_SOCKET_HAD_TIMEOUT = SocketError("Read Timeout")
ERR_SOCKET_HAD_ERROR = SocketError("Read Failure")

# recv_one_line attempts to read() data from socket connection, repeatedly,
# until a "\r\n" pair is detected. It returns all the data received as a python
# string, not including the terminating "\r\n" pair. If something went wrong,
# then a special value is returned instead:
# - ERR_SOCKET_WAS_CLOSED is returned if the connection was closed unexpectedly
# - ERR_SOCKET_HAD_TIMEOUT is returned if no data was received for 3 seconds
# - ERR_SOCKET_HAD_ERROR is returned if som other error occurred
def read_one_line(connection):
    # Set 3 second timeout, so we don't wait for data forever
    connection.settimeout(3.0)
    try:
        data = ""
        # Keep reading from socket until we get a "\r\n" pair.
        while not data.endswith("\r\n"):
            # Read one more byte from socket, append it to our data.
            more_data = connection.recv(1)
            if not more_data:
                return ERR_SOCKET_WAS_CLOSED
            data += more_data.decode() # decode byte as an ascii character
        # Return the accumulated data, without the terminating "\r\n" sequence.
        return data[:-2]
    except socket.timeout as err:
        return ERR_SOCKET_HAD_TIMEOUT
    except:
        print("Error reading from socket: " + traceback.format_exc())
        return ERR_SOCKET_HAD_ERROR
    finally:
        # Remove the timeout, so future operations are not affected by this.
        connection.settimeout(None)

# Get command-line parameters, if present
if len(sys.argv) != 3:
    print("Sorry, this program requires 2 arguments, like this:")
    print("%s addr port -- connects to given server address and port" % sys.argv[0])
    sys.exit(1)
server_host = sys.argv[1]
server_port = int(sys.argv[2])

# Print a welcome message
print("Starting POP3 client")
print("Connecting to server %s on port %d" % (server_host, server_port))

# Create a client socket, and connect it to the server
server_addr = (server_host, server_port)
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect(server_addr)

print("Connected!")
print()

# Finally, the main user-interaction loop.
try:

    # Next, repeatedly get user input and send it to the server,
    # then print whatever response the server sends back.
    while True:
        # get user input
        try:
            cmd = input()
        except:
            break
        if cmd.startswith("send "):
            line = cmd[5:]
            # if user input is non-blank, send it to the server
            connection.sendall((line + "\r\n").encode())
            print("sent: " + line)
        elif cmd.startswith("s "):
            line = cmd[2:]
            # if user input is non-blank, send it to the server
            connection.sendall((line + "\r\n").encode())
            print("sent: " + line)
        elif cmd == "recv" or cmd == "r":
            # otherwise, user input is blank, so try to receive data instead
            resp = read_one_line(connection)
            if resp == ERR_SOCKET_WAS_CLOSED:
                print("Remote connection lost.")
                break
            elif resp == ERR_SOCKET_HAD_ERROR:
                print("Error with connection.")
                break
            elif resp == ERR_SOCKET_HAD_TIMEOUT:
                print("Timeout, no data received.")
            else:
                print("recv: " + resp)
        elif cmd == "fail":
            # this is only for stress-testing the pop-server
            connection.sendall(b"\r\n")
            print("recv: " + read_one_line(connection))
            connection.sendall(b" \r\n")
            print("recv: " + read_one_line(connection))
            connection.sendall(b" \n  \r\n")
            print("recv: " + read_one_line(connection))
            connection.sendall(b"xyz")
            break
        else:
            print("To send data, type \"send\" or \"s\" followed by some text, then hit enter.")
            print("To receive data, type \"recv\" or \"r\", then hit enter.")
            print("To quit, use Control-C or Control-D.")

finally:
    print("Closing socket connection to server")
    connection.close()

print("Done")
