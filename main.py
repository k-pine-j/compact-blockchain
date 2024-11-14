import multiprocessing
import time
from node import Node

if __name__ == "__main__":
    # Node 1を起動
    node_1 = Node(node_id=1, host="localhost", port=5001, peers=[("localhost", 5002), ("localhost", 5003), ("localhost", 5004)])
    process_1 = multiprocessing.Process(target=node_1.start)
    process_1.start()
    print("Node 1 started.")

    # 30秒待機
    time.sleep(30)

    # Node 2とNode 3を起動
    node_2 = Node(node_id=2, host="localhost", port=5002, peers=[("localhost", 5001), ("localhost", 5003), ("localhost", 5004)])
    node_3 = Node(node_id=3, host="localhost", port=5003, peers=[("localhost", 5001), ("localhost", 5002), ("localhost", 5004)])
    # 不正なノードを起動
    invalid_node = Node(node_id=4, host="localhost", port=5004, peers=[("localhost", 5001), ("localhost", 5002), ("localhost", 5003)], is_invalid_node=True)

    process_2 = multiprocessing.Process(target=node_2.start)
    process_3 = multiprocessing.Process(target=node_3.start)
    process_4 = multiprocessing.Process(target=invalid_node.start)

    process_2.start()
    process_3.start()
    process_4.start()
    
    print("Node 2 and Node 3 started after 30 seconds delay.")

    print("Invalid Node started.")

    # 全てのプロセスが終了するのを待機
    process_1.join()
    process_2.join()
    process_3.join()
    process_4.join()
