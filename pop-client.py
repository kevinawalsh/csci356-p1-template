#!/usr/bin/python3

# Author: K. Walsh <kwalsh@cs.holycross.edu>
# Date: 20 August 2020
#
# A simple POP3 client from scratch in Python. Run it like this:
#   ./pop3-client.py example.com
#
# It will connect to port 110, the standard POP3 port, by default. If you want
# to use a different port (e.g. port 12345), you can run it like this:
#   ./pop3-client.py example.com 12345
#
# Note: This code is not "pythonic" at all; there are more concise ways to write
# this code by using python features like dicts and string interpolation. We
# also avoid use of any modules except for a few basic ones.

import socket    # for socket stuff
import sys       # for sys.argv
import traceback # for printing exceptions

# Global configuration variables, with default values
server_host = None
server_port = 110


# recv_one_line reads() data from socket c until a "\r\n" prair is detected. It
# returns all the data received as a python string, not including the
# terminating "\r\n" pair.
def read_one_line(c):
    data = ""
    # Keep reading from socket until we get a "\r\n" pair.
    while not data.endswith("\r\n"):
        # Read one more byte from socket, append it to our data.
        try:
            more_data = c.recv(1)
            if not more_data:
                print("Socket connection was lost")
                return None
            data += more_data.decode() # decode byte as an ascii character
        except:
            print("Error reading from socket: " + traceback.format_exc())
            return None
    # Return the accumulate data, without the terminating "\r\n" sequence.
    return data[:-2]


# Get command-line parameters, if present
if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Sorry, this program only accepts 1 or 2 arguments.")
    print("Usage: %s address [port]" % sys.argv[0])
    sys.exit(1)
server_host = sys.argv[1]
if len(sys.argv) >= 3:
    server_port = int(sys.argv[2])


# Print a welcome message
print("Starting POP3 client")
print("Connecting to server %s on port %d" % (server_host, server_port))


# Create a client socket, and connect it to the server
server_addr = (server_host, server_port)
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect(server_addr)

# Finally, the main user-interaction loop.
try:
    # Server sends a greeting first thing, so receive that and print it
    greeting = read_one_line(c)
    if greeting is None:
        print("Oops, no greeting?!")
        sys.exit(0)
    print("Greeting from server: " + greeting)

    # Next, repeatedly get user input and send it to the server,
    # then print whatever response the server sends back.
    while True:
        # get user input
        cmd = input("cmd? ")
        # send it to server, but if user just hit enter, don't send the blank
        # input (that way user can just hit enter to get another response from
        # server, or a continuation of some previous response, without actually
        # sending another command)
        if cmd:
            c.sendall((cmd + "\r\n").encode())
        # get response from server
        resp = read_one_line(c)
        # print it
        if resp is None:
            print("Oops, no respose?!")
            break
        print("Response: " + resp)

finally:
    print("Closing socket connection to server")
    c.close()

print("Done")
