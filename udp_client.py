import socket
import hashlib  # needed to calculate the SHA256 hash of the file
import sys  # needed to get cmd line parameters
import os.path as path  # needed to get size of file in bytes


IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_size(file_name: str) -> int:
    size = 0
    try:
        size = path.getsize(file_name)
    except FileNotFoundError as fnfe:
        print(fnfe)
        sys.exit(1)
    return size


def send_file(filename: str):
    # get the file size in bytes
    file_size = get_file_size(filename)
    # convert the file size to an 8-byte byte string using big endian
    size = file_size.to_bytes(8, byteorder='big')
    # create a SHA256 object to generate hash of file
    file_hash=hashlib.sha256(filename.encode())

    # create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # send the file size in the first 8-bytes followed by the bytes
        # for the file name to server at (IP, PORT)
        client_socket.sendto(size + filename.encode(), (IP, PORT))
        response, server_address = client_socket.recvfrom(BUFFER_SIZE)
        if response != b'go ahead':
            raise Exception('Bad server response - was not go ahead!')
        with open(filename, 'rb') as file:
            chunk = file.read(BUFFER_SIZE)


            # read the file in chunks and send each chunk to the server
            while len(chunk) > 0:
                file_hash.update(chunk)
                client_socket.sendto(chunk, (IP, PORT))
                chunk = file.read(BUFFER_SIZE)
                response2, server_address = client_socket.recvfrom(BUFFER_SIZE)
                if response2 != b'received':
                    raise Exception('Bad server response - was not received')
                    pass  # replace this line with your code

        # send the hash value so server can verify that the file was
        # received correctly.
        hashResponse, server_address = client_socket.recvfrom(BUFFER_SIZE)
        if hashResponse == b'send hash':
            client_socket.sendto(file_hash.digest(), server_address)
        response3, server_address = client_socket.recvfrom(BUFFER_SIZE)
        if response3 == b'failed':
            raise Exception('Transfer failed!')
        else:
            print('Transfer completed!')
    except Exception as e:
        print(f'An error occurred while sending the file: {e}')
    finally:
        client_socket.close()

if __name__ == "__main__":
    # get filename from cmd line

    if len(sys.argv) < 2:
        print(f'SYNOPSIS: {sys.argv[0]} <filename>')
        sys.exit(1)
    file_name = sys.argv[1]  # filename from cmdline argument
    send_file(input('Enter filepath: '))

