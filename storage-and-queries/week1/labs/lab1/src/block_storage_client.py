import os
import socket
import shutil
from tqdm.notebook import tqdm


def create_folder(path: str):
    """Create a folder, if it exists delete it and recreate it.

    Args:
        path (str): Path to folder
    """
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        # Removes all the subdirectories!
        shutil.rmtree(path)
        os.makedirs(path)


class BlockStorageClient:
    """Emulates a Block storage client that is able to connect with a remote
    server.
    """
    def __init__(self, server_ip, server_port, block_size: int = 16384):
        self.server_ip = server_ip
        self.server_port = server_port
        self.block_size = block_size
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.files_folder = os.path.join(dir_path, 'client_files')
        self.blocks_folder = os.path.join(dir_path, 'client_blocks')
        create_folder(self.files_folder)
        create_folder(self.blocks_folder)

    def connect(self):
        """Connects with BlockStorageServer
        """
        try:
            print(f"Connecting to {self.server_ip}:{self.server_port}")
            self.client_socket.settimeout(20)
            self.client_socket.connect((self.server_ip, self.server_port))
            self.handshake()
        except socket.error as msg:
            print(f"Failed to connect: {msg}")
        else:
            print(f"Connected to {self.server_ip}:{self.server_port}")


    def handshake(self):
        """Perform Handshake with the BlockStorageServer

        Raises:
            Exception: Raises if handshake fails
        """
        self.send_string("Negotiate")
        negotiation_response = self.receive_string()
        if negotiation_response != "OK":
            raise Exception("Negotiation failed")
        # Receive negotiation response containing the agreed block size
        self.client_socket.sendall(self.block_size.to_bytes(4, 'big'))
        print("Handshake done")

    def send_string(self, string: str):
        """Send a given string to the server

        Args:
            string (str): String to send
        """
        self.client_socket.sendall(len(string).to_bytes(4, 'big'))
        self.client_socket.sendall(string.encode())

    def receive_string(self):
        """Receive a given string from the server
        """
        str_len = int.from_bytes(self.client_socket.recv(4), 'big')
        str_decoded = self.client_socket.recv(str_len).decode()
        return str_decoded

    def list_files(self):
        """List files available in the BlockStorageServer

        Returns:
            files: List of file names
        """
        self.send_string("list")
        file_count = int.from_bytes(self.client_socket.recv(4), 'big')
        if file_count > 0:
            self.send_string("OK")
        files = []
        for _ in range(file_count):
            file_name = self.receive_string()
            files.append(file_name)
        return files

    def send_file(self, file_path: str, verbose: bool = True):
        """Divides a file in fixed blocks and sends them to the server

        Args:
            file_path (str): Path to the file
        """
        file_name = os.path.basename(file_path)
        self.send_string("send")
        self.send_string(file_name)
        if verbose:
            blocks_path = os.path.join(self.blocks_folder,
                                       os.path.splitext(file_name)[0])
            create_folder(blocks_path)
            block_count = 0
        try:
            file_size = os.path.getsize(file_path)
            self.client_socket.sendall(file_size.to_bytes(4, 'big'))
            with open(file_path, 'rb') as file:
                while True:
                    block = file.read(self.block_size)
                    if not block:
                        break
                    self.client_socket.sendall(block)
                    if verbose:
                        block_path = os.path.join(blocks_path,
                                                  f'block_{block_count}.dat')
                        with open(block_path, 'wb') as block_file:
                            block_file.write(block)
                        block_count += 1
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def receive_file(self, file_name: str, verbose: bool = True):
        """Receive a file in fixed blocks and reconstruct it.

        Args:
            file_name (str): Name of the file
        """
        self.send_string("receive")
        self.send_string(file_name)
        response = self.receive_string()
        if response != "OK":
            print(f'{file_name} does not exists in server')
            return
        file_path = os.path.join(self.files_folder, file_name)
        if verbose:
            blocks_path = os.path.join(self.blocks_folder,
                                       os.path.splitext(file_name)[0])
            create_folder(blocks_path)
        block_count = 0
        remaining = int.from_bytes(self.client_socket.recv(4), 'big')
        blocks_count = remaining//self.block_size + 1
        print(f"Receiving {blocks_count} blocks")
        try:
            pbar = tqdm(total=blocks_count)
            with open(file_path, 'wb') as file:
                while remaining > 0:
                    block = self.client_socket.recv(min(remaining,
                                                        self.block_size))
                    remaining -= len(block)
                    if verbose:
                        block_file_name = f'block_{block_count}.dat'
                        block_path = os.path.join(blocks_path,
                                                  block_file_name)
                        with open(block_path, 'wb') as block_file:
                            block_file.write(block)
                    block_count += 1
                    pbar.update(1)
                    file.write(block)
            pbar.close()
            print("File received successfully.")
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close(self):
        """Closes the connection with the BlockStorageServer
        """
        self.client_socket.close()


def main():
    server_ip = '127.0.0.1'  # Change this to your server's IP address
    server_port = 9090  # Change this to your server's port
    file_path = 'employees.csv'  # Path to the file you want to send
    client = BlockStorageClient(server_ip, server_port)
    client.connect()
    client.send_file(file_path)
    file_list = client.list_files()
    print(file_list)
    if len(file_list) > 0:
        client.receive_file(file_list[0])
    client.close()


if __name__ == "__main__":
    main()
