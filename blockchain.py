import hashlib
import time
import csv

MAX_TARGET = 0xFFFF * 2**224  # ターゲットを緩くするためビット数を調整

class Block:
    def __init__(self, index, previous_hash, transactions, nonce=0, timestamp=None, hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.nonce = nonce
        self.hash = hash or self.compute_hash()

    def compute_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.transactions}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self):
        return (f"Block(Index: {self.index}, Hash: {self.hash[:10]}..., "
                f"Previous: {self.previous_hash[:10]}..., "
                f"Transactions: {self.transactions}, Nonce: {self.nonce})")

class Blockchain:
    def __init__(self, chain, node_id, difficulty=5, target_block_time=10):
        self.chain = chain
        self.node_id = node_id
        self.difficulty = difficulty
        self.target_block_time = target_block_time

    def add_genesis_block(self):
        genesis_block = Block(0, "0", [])
        genesis_block.hash = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)
        print(f"Genesis Block Created: {genesis_block}")
        return genesis_block

    def add_block(self, transactions):
        if not self.chain:
            print("No genesis block found; aborting block addition.")
            return None

        previous_block = self.chain[-1]
        new_index = previous_block.index + 1
        new_block = Block(new_index, previous_block.hash, transactions)
        
        new_block.hash = self.proof_of_work(new_block)
        if self.is_valid_block(new_block, previous_block):
            self.chain.append(new_block)
            print(f"Block Added: {new_block}")
            self.adjust_difficulty()
            return new_block
        else:
            print("Block validation failed.")
        return None

    def calculate_target(self):
        target = MAX_TARGET // (2 ** (self.difficulty - 1))
        return target

    def proof_of_work(self, block):
        target = self.calculate_target()
        block.nonce = 0
        while True:
            computed_hash = block.compute_hash()
            if int(computed_hash, 16) < target:
                return computed_hash
            block.nonce += 1

    def is_valid_block(self, block, previous_block):
        target = self.calculate_target()
        return (block.previous_hash == previous_block.hash 
                and int(block.hash, 16) < target
                and block.hash == block.compute_hash())

    def adjust_difficulty(self):
        if len(self.chain) > 1:
            last_block = self.chain[-1]
            previous_block = self.chain[-2]
            time_taken = last_block.timestamp - previous_block.timestamp
            
            if time_taken < self.target_block_time:
                self.difficulty += 1
                print("Difficulty increased to", self.difficulty)
            elif time_taken > self.target_block_time:
                self.difficulty = max(1, self.difficulty - 1)
                print("Difficulty decreased to", self.difficulty)

    def export_chain_to_csv(self, filename=None):
        # ブロックチェーンのデータをCSVファイルにエクスポートする"""
        filename = filename or f"node_{self.node_id}_blockchain.csv"
        with open(filename, mode='w', newline='') as csv_file:
            fieldnames = ['index', 'timestamp', 'previous_hash', 'hash', 'transactions', 'nonce']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for block in self.chain:
                writer.writerow({
                    'index': block.index,
                    'timestamp': block.timestamp,
                    'previous_hash': block.previous_hash,
                    'hash': block.hash,
                    'transactions': block.transactions,
                    'nonce': block.nonce
                })