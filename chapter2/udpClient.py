import socket;

target_host = "222.google.com";
target_port = 80;

# create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);

# send data
client.sendto("UDP Data", (target_host, target_port));

# receive data
data, addr = client.recvfrom(4096);

print data;