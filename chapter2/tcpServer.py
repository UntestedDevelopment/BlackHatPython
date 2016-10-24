import socket;
import threading;

bind_ip   = "0.0.0.0";
bind_port = 9999;

# create socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

server.bind((bind_ip, bind_port));

# listen for connections
# max backlog 5
server.listen(5);

print "[*] Listening on %s:%d" % (bind_ip, bind_port);

# client handling function
def handle_client(client_socket):
    # print whatever the client sends
    request = client_socket.recv(1024);

    print "[*] received %s" % request

    # send response to acknowledge we received the request
    client_socket.send("ACK!");

    client_socket.close()


while True:
    # accept next request
    client, addr = server.accept();

    print "[*] Accepted connection from %s:%d" % (addr[0], addr[1]);

    # create a thread to handle request
    client_handler = threading.Thread(target=handle_client, args=(client,));
    client_handler.start(); 


