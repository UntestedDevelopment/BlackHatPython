import getopt
import socket
importsubprocess
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
        opts, args = getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
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
                port = a
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
        
main()