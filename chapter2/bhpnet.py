import getopt
import socket
import subprocess
import sys
import threading

# global variables
listen             = False
command            = False
upload             = False
execute            = ""
target             = ""
upload_destination = ""
port               = 9999


# print help 
def usage():
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen                    - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run       - execute the given command upon receiving a connection"
    print "-c --commandshell              - initialize a command shell"
    print "-u --upload=destination        - upon receiving a connection upload file and write to [destination]"
    print
    print
    print "Examples:"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "echo 'ABCDEFG' | ./bhpnet.py -t 192.168.0.1 -p 5555"
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    # show help if no parameters specified
    if not len(sys.argv[1:]):
        usage()

    # read the parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
            if o in ("-h", "--help"):
                usage()
            elif o in ("-l", "--listen"):
                listen = True
            elif o in ("-e", "--execute"):
                execute = a
            elif o in ("-c", "--commandshell"):
                command = True
            elif o in ("-u", "--upload"):
                upload_destination = a
            elif o in ("-t", "--target"):
                target = a
            elif o in ("-p", "--port"):
                port = int(a)
            else:
                assert False, "Unhandled Option"

    # are we listening or sending data from stdin?
    if not listen and len(target) and port > 0:
        # read into the buffer from the commandline
        # this will block, so send ctrl-D if not sending input to stdin
        buffer = sys.stdin.read()

        # send data
        client_sender(buffer)

    # we are listening and potentially going to upload things
    # execute commands or get a shell depending in the options above
    if listen:
        server_loop()

def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            # read the reponse
            recv_len = 1
            response = ""

            while recv_len:
                data      = client.recv(4096)
                recv_len  = len(data)
                response += data

                # end of response?
                if recv_len < 4096:
                    break

            print response

            # wait for more input
            buffer  = raw_input("")
            buffer += "\n"

            # send to client
            client.send(buffer)

    except:
        print "[*] Exception! Exiting."

        # tear down the connection
        client.close()

def server_loop():
    global target

    # if no target is defined listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    print "%s:%s" % (target, port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin up thread to handle the new client 
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    # trim the newline
    command = command.rstrip()

    # run the command and retreive the output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "failed to execute command. \r\n"

    return output
 

def client_handler(client_socket):
    global upload
    global execute
    global command

    #check for upload
    if len(upload_destination):
        # read until we can read no more
        file_buffer = ""

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        # write the buffer to a file
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("failed to save file to %s\r\n" % upload_destination)

    # check for command exec
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    # check for shell request
    if command:
        while True:
            # show command prompt
            client_socket.send("<BHP:#> ")

            # receive until enter key hit
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer +=client_socket.recv(1024)

            response = run_command(cmd_buffer)
            client_socket.send(response)




main()