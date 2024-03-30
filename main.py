# import json
# import os
# import hashlib
# from multiprocessing import Pool

# def read_transaction(file_path):
#     with open(file_path, 'r') as file:
#         return json.load(file)

# def is_valid_transaction(transaction):
#     if not all(key in transaction for key in ["version", "locktime", "vin", "vout"]):
#         return False
#     return True

# def create_coinbase_tx(miner_address, block_reward):
#     return {"vin": [{"coinbase": "coinbase"}], "vout": [{"value": block_reward, "address": miner_address}]}

# def serialize_tx(tx):
#     return json.dumps(tx, sort_keys=True)

# def calculate_txid(serialized_tx):
#     return hashlib.sha256(serialized_tx.encode()).hexdigest()

# def calculate_block_hash(nonce, transactions):
#     block_content = str(nonce) + ''.join(transactions)
#     return hashlib.sha256(block_content.encode()).hexdigest()

# def mine_block(transactions, difficulty_target):
#     nonce = 0
#     print_update_interval = 100  # Update the terminal every 100 nonce attempts

#     while True:
#         if nonce % print_update_interval == 0:
#             print(f"Trying nonce: {nonce}")
        
#         block_hash = calculate_block_hash(nonce, transactions)
#         if int(block_hash, 16) < int(difficulty_target, 16):
#             print(f"Nonce found: {nonce}, Block Hash: {block_hash}")
#             return nonce, block_hash
#         nonce += 1


# def main(mempool_folder, miner_address, block_reward, difficulty_target, output_file):
#     transactions = []
#     txids = []
#     files_processed = 0  # Counter for the files processed

#     for filename in os.listdir(mempool_folder):
#         file_path = os.path.join(mempool_folder, filename)
#         transaction = read_transaction(file_path)
#         if is_valid_transaction(transaction):
#             serialized_tx = serialize_tx(transaction)
#             txid = calculate_txid(serialized_tx)
#             transactions.append(serialized_tx)
#             txids.append(txid)
#             files_processed += 1  # Increment the counter each time a file is processed
#             # Print the transaction's details in real-time
#             print(f"Processed transaction {files_processed}: {txid}")

#     coinbase_tx = create_coinbase_tx(miner_address, block_reward)
#     serialized_coinbase_tx = serialize_tx(coinbase_tx)
#     coinbase_txid = calculate_txid(serialized_coinbase_tx)
#     transactions.insert(0, serialized_coinbase_tx)
#     txids.insert(0, coinbase_txid)

#     print("Starting to mine the block with the transactions...")
#     nonce, block_hash = mine_block(transactions, difficulty_target)
#     print(f"Block mined! Nonce: {nonce}, Block Hash: {block_hash}")

#     with open(output_file, 'w') as file:
#         file.write(f"Block Hash: {block_hash}, Nonce: {nonce}\n")
#         file.write(f"{serialized_coinbase_tx}\n")
#         file.writelines("\n".join(txids))

#     print(f"Finished! {len(txids)} transactions were included in the block.")

# if __name__ == "__main__":
#     mempool_folder = './mempool'  # Adjust based on your folder structure
#     miner_address = '1BitcoinAddress'
#     block_reward = 6.25  # Example block reward
#     difficulty_target = '0000ffff00000000000000000000000000000000000000000000000000000000'
#     output_file = 'output.txt'

#     main(mempool_folder, miner_address, block_reward, difficulty_target, output_file)

import json
import os
import hashlib

# Assuming functions for digital signature verification and UTXO checks
def verify_signature(transaction):
    # Placeholder for signature verification logic
    return True

def is_in_utxo(input, utxo_set):
    # Placeholder for UTXO set check
    return input in utxo_set

def is_double_spending(transaction, mempool):
    # Placeholder for double spending check within the mempool
    return False

def read_transaction(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def is_valid_transaction(transaction):
    required_fields = ["id", "inputs", "outputs", "signature"]
    return all(field in transaction for field in required_fields)

def create_coinbase_tx(miner_address, block_reward):
    return {"id": "coinbase", "inputs": [], "outputs": [{"value": block_reward, "address": miner_address}], "signature": ""}

def serialize_tx(tx):
    return json.dumps(tx, sort_keys=True)

def calculate_txid(serialized_tx):
    return hashlib.sha256(serialized_tx.encode()).hexdigest()

def calculate_block_hash(nonce, transactions):
    block_content = str(nonce) + ''.join(transactions)
    return hashlib.sha256(block_content.encode()).hexdigest()

def mine_block(transactions, difficulty_target):
    nonce = 0
    print("Starting mining...")
    while True:
        block_hash = calculate_block_hash(nonce, transactions)
        if int(block_hash, 16) < int(difficulty_target, 16):
            print(f"Nonce found: {nonce}, Block Hash: {block_hash}")
            return nonce, block_hash
        nonce += 1

def validate_and_serialize_transaction(transaction, utxo_set, mempool):
    if not is_valid_transaction(transaction):
        return None, "Invalid transaction format."
    if not verify_signature(transaction):
        return None, "Invalid signature."
    if is_double_spending(transaction, mempool):
        return None, "Double spending detected."

    # Check transaction inputs against UTXO set
    total_input_value = sum(utxo_set[input]['value'] for input in transaction['inputs'] if is_in_utxo(input, utxo_set))
    total_output_value = sum(output['value'] for output in transaction['outputs'])
    if total_input_value < total_output_value:
        return None, "Insufficient input value."

    return serialize_tx(transaction), "Transaction validated."

def main(mempool_folder, miner_address, block_reward, difficulty_target, output_file):
    utxo_set = {}  # Placeholder for the UTXO set
    mempool = []  # Placeholder for the mempool transactions
    transactions = []
    txids = []

    # Add coinbase transaction
    coinbase_tx = create_coinbase_tx(miner_address, block_reward)
    transactions.append(serialize_tx(coinbase_tx))
    txids.append(calculate_txid(serialize_tx(coinbase_tx)))

    for filename in os.listdir(mempool_folder):
        file_path = os.path.join(mempool_folder, filename)
        transaction = read_transaction(file_path)
        serialized_tx, message = validate_and_serialize_transaction(transaction, utxo_set, mempool)
        if serialized_tx:
            transactions.append(serialized_tx)
            txids.append(calculate_txid(serialized_tx))
            print(f"Transaction {calculate_txid(serialized_tx)} validated and added.")
        else:
            print(f"Transaction from {filename} skipped: {message}")

    nonce, block_hash = mine_block(transactions, difficulty_target)

    with open(output_file, 'w') as file:
        file.write(f"Block Hash: {block_hash}, Nonce: {nonce}\n")
        file.writelines(f"{tx}\n" for tx in transactions)

    print(f"Finished! Block mined with {len(txids)} transactions included.")

if __name__ == "__main__":
    mempool_folder = './mempool'
    miner_address = '1BitcoinAddress'
    block_reward = 6.25
    difficulty_target = '0000ffff00000000000000000000000000000000000000000000000000000000'
    output_file = 'output.txt'

    main(mempool_folder, miner_address, block_reward, difficulty_target, output_file)
