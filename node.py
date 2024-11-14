import socket
import threading
import pickle
import time
import random
import multiprocessing
from blockchain import Blockchain
from external_transactions import generate_transaction

class Node:
    def __init__(self, node_id, host, port, peers, block_limit=100, is_invalid_node=False):
        self.node_id = node_id
        self.is_invalid_node = is_invalid_node # 不正なノードを確認するパラメータ
        self.blockchain = Blockchain(node_id=node_id, chain=[], is_invalid_node=self.is_invalid_node)
        self.host = host
        self.port = port
        self.peers = peers
        self.block_limit = block_limit
        self.generated_blocks = 0
        self.stop_mining = False
        self.mining_delay = random.uniform(1, 5)  # ブロック生成間隔を長めに設定
        self.initial_sync = True

    def start(self):
        threading.Thread(target=self.run_server).start()
        time.sleep(5)

        # Node 1のみがジェネシスブロックを生成
        if self.node_id == 1:
            if len(self.blockchain.chain) == 0:
                self.blockchain.add_genesis_block()
                print(f"Node {self.node_id} generated the Genesis Block")
        else:
            # Node 2, 3, 4が起動時に最長チェーンをリクエストして同期
            self.request_longest_chain()

        # 定期的なチェーン同期を開始
        self.start_periodic_sync()

        # マイニングプロセスを開始
        p = multiprocessing.Process(target=self.mine_blocks)
        p.start()
        p.join()

    def start_periodic_sync(self):
        # 一定時間ごとに他のノードから最長チェーンを取得して同期する
        threading.Thread(target=self.periodic_sync).start()

    def periodic_sync(self):
        while True:
            time.sleep(30)  # 30秒ごとにチェーンの長さを確認して同期
            self.request_longest_chain()
            self.blockchain.export_chain_to_csv()


    def request_longest_chain(self):
        longest_chain = []
        max_length = len(self.blockchain.chain)

        for peer_host, peer_port in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer_host, peer_port))
                    s.sendall(pickle.dumps("REQUEST_CHAIN"))

                    data = b""
                    while True:
                        packet = s.recv(4096)
                        if not packet:
                            break
                        data += packet

                    if data:
                        try:
                            peer_chain = pickle.loads(data)
                            # チェーン全体の妥当性を確認
                            valid_chain = all(
                                self.blockchain.is_valid_block(peer_chain[i], peer_chain[i - 1])
                                for i in range(1, len(peer_chain))
                            )
                            if valid_chain and len(peer_chain) > max_length:
                                longest_chain = peer_chain
                                max_length = len(peer_chain)
                                print(f"Node {self.node_id} found a suitable chain from {peer_host}:{peer_port}")
                        except pickle.UnpicklingError:
                            print(f"Node {self.node_id} received truncated or invalid pickle data from {peer_host}:{peer_port}")
                            continue
            except ConnectionRefusedError:
                print(f"Node {self.node_id} could not connect to {peer_host}:{peer_port}")

        if longest_chain:
            self.blockchain.chain = longest_chain
            print(f"Node {self.node_id} synchronized to the longest chain with {len(longest_chain)} blocks.")


    def mine_blocks(self):
        while self.generated_blocks < self.block_limit:
            if self.stop_mining:
                print(f"Node {self.node_id} is paused waiting for chain sync.")
                self.stop_mining = False
                time.sleep(2)
                continue

            # 同期してからブロックを生成
            self.request_longest_chain()

            # ノードタイプに応じて正常または不正なトランザクションを生成
            if self.is_invalid_node:
                transactions = [{"sender": "InvalidUser", "receiver": "User0", "amount": -50}]
                print(f"Node {self.node_id} generated an invalid transaction.")
            else:
                transactions = [generate_transaction() for _ in range(3)]
            new_block = self.blockchain.add_block(transactions)

            if new_block:
                self.broadcast_block(new_block)
                self.await_block_acknowledgment(new_block)  # ブロックの受信確認
                self.generated_blocks += 1
                print(f"Node {self.node_id} generated block {self.generated_blocks}")
            else:
                print(f"Node {self.node_id} waiting for the latest block sync.")
                time.sleep(2)

            time.sleep(self.mining_delay)
            self.blockchain.export_chain_to_csv()
        print(f"Node {self.node_id} has reached its block generation limit.")

    def broadcast_block(self, block):
        # 生成したブロックを他のノードにブロードキャストする
        if block is None:
            print(f"Node {self.node_id} cannot broadcast a None block.")
            return

        data = pickle.dumps(block)
        for peer_host, peer_port in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer_host, peer_port))
                    s.sendall(data)
                print(f"Node {self.node_id} broadcasted block {block.index} to {peer_host}:{peer_port}")
            except ConnectionRefusedError:
                print(f"Node {self.node_id} failed to connect to {peer_host}:{peer_port} for block broadcast")

    def await_block_acknowledgment(self, block):
        # ブロードキャスト後、他ノードが新しいブロックを受信するまで待機
        time.sleep(5)  # 少し待機して、他のノードが同期する時間を確保

    def run_server(self):
        # ノードのサーバーを実行し、他ノードからのリクエストを処理する"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Node {self.node_id} running on {self.host}:{self.port}")
        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        # 他のノードからのリクエストを処理する"""
        data = client_socket.recv(4096)
        message = pickle.loads(data)

        if message == "REQUEST_CHAIN":
            try:
                client_socket.sendall(pickle.dumps(self.blockchain.chain))
            except pickle.PicklingError:
                print(f"Node {self.node_id} failed to send chain data due to pickling error.")
        else:
            # ブロックデータとして処理
            block = message
            if block is None:
                print(f"Node {self.node_id} received an invalid block.")
                client_socket.close()
                return

            if any(existing_block.index == block.index for existing_block in self.blockchain.chain):
                print(f"Node {self.node_id} rejected block {block.index} due to index conflict.")
                client_socket.close()
                return

            if block not in self.blockchain.chain:
                self.stop_mining = True
                self.blockchain.chain.append(block)
                print(f"Node {self.node_id} accepted block {block.index} and paused mining for sync.")
                self.broadcast_block(block)
                self.stop_mining = False

        client_socket.close()
