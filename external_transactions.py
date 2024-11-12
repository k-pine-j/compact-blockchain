import csv
import random

# トランザクションの送信者、受信者、金額をランダムに生成する関数
def generate_transaction():
    sender = f"User{random.randint(1, 100)}"
    receiver = f"User{random.randint(1, 100)}"
    amount = random.randint(1, 100)

    # トランザクションデータを辞書として定義
    transaction = {
        'sender': sender,
        'receiver': receiver,
        'amount': amount
    }

    # トランザクションをCSVに追記
    save_transaction_to_csv(transaction)

    return transaction

# トランザクションをCSVに保存する関数
def save_transaction_to_csv(transaction, filename="transactions.csv"):
    # ヘッダーがまだ書かれていない場合のためにファイルを開くモードを確認
    file_exists = False
    try:
        with open(filename, 'x', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['sender', 'receiver', 'amount'])
            writer.writeheader()
            writer.writerow(transaction)
            file_exists = True
    except FileExistsError:
        pass  # ファイルが既に存在する場合はヘッダーを書き込まない

    # ファイルが既に存在している場合は追記モードで書き込み
    if not file_exists:
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['sender', 'receiver', 'amount'])
            writer.writerow(transaction)
