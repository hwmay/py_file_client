py_file_client
==============

Simple file client and server written in Python

Usage:

On server site start the server with python py_file_server.py <port>
When omitting a port, 50007 is the standard port and set by the server.

On client site start the client with python py_file_client.py
Enter the IP address and the port number and change the home directory (where the downloaded files will be saved) as needed.


With the graphical client you can navigate thru the server and download files to the client, assumed the user who has started the server has the access rights.

The client window is splitted in two halfs: on the left site you see the files and directories on the server, the right site shows a journal of your actions respectively error messages from the server.

For navigation double click on a server directory for entering it. Press the up button for moving up one directory level. Alternatively the directory on the server can be entered manually. 

For downloading mark the files and press the get files button.


py_file_client is available in english and german, the server only in english.
