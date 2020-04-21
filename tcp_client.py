import socket

def recvline(conn):
    """
    receive data from socket until newline
    """
    buf = b''
    while True:
        c = conn.recv(1)
        if c == b"\n":
            break
        buf += c
    return buf.decode()

def sendline(conn, s):
    """
    send data with newline
    """
    b = (s + "\n").encode()
    conn.send(b)




host = "localhost"
port = 8888
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((host, port))
sendline(conn,"hello")
print(recvline(conn))