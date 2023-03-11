import socket
import os
import hashlib  # needed to verify file hash


IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_info(data: bytes) -> (str, int):
    return data[8:].decode(), int.from_bytes(data[:8],byteorder='big')


def upload_file(server_socket: socket, file_name: str, file_size: int):
    # create a SHA256 object to verify file hash
    hsh = hashlib.sha256(file_name.encode())
    # create a new file to store the received data
    with open(file_name+'.temp', 'wb') as file:
        try:
            while True:
                server_socket.setblocking(0)
                ready = select.select([server_socket], [], [], 1)
                if ready[0]:
                    chunk, client_address = server_socket.recvfrom(BUFFER_SIZE)
                else:
                    server_socket.setblocking(1)
                    break
                file.write(chunk)
                hsh.update(chunk)
                server_socket.sendto(b'received', client_address)
                if len(chunk) < 1:
                    print('k')
                    break
        except KeyboardInterrupt as ki:
            print("Shutting down...")

    # get hash from client to verify
    server_socket.setblocking(1)
    server_socket.sendto(b'send hash', client_address)
    response2, client_address = server_socket.recvfrom(BUFFER_SIZE)
    if response2 == hsh.digest():
        server_socket.sendto(b'success', client_address)
    else:
        os.remove(file_name + '.temp')
        server_socket.sendto(b'failed', client_address)


def start_server():
    # create a UDP socket and bind it to the specified IP and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f'Server ready and listening on {IP}:{PORT}')

    try:
        while True:
            name, client_address = server_socket.recvfrom(BUFFER_SIZE)
            file_size = get_file_info(name)[1]
            file_name = get_file_info(name)[0]
            server_socket.sendto(b'go ahead', client_address)
            upload_file(server_socket, file_name, file_size)
            break
    except KeyboardInterrupt as ki:

        pass
    except Exception as e:
        print(f'An error occurred while receiving the file:str {e}')
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()
