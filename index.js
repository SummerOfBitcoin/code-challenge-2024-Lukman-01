const fs = require('fs');
const crypto = require('crypto');
const secp256k1 = require('secp256k1');

// Constants
const TARGET_DIFFICULTY = BigInt('0x0000ffff00000000000000000000000000000000000000000000000000000000');

// Function to validate a transaction
function isValidTransaction(transaction) {
    // Check if transaction has required fields
    if (!transaction.sender || !transaction.receiver || !transaction.amount || !transaction.signature) {
        return false;
    }

    // Verify signature
    const message = transaction.sender + transaction.receiver + transaction.amount;
    const publicKey = Buffer.from(transaction.senderPublicKey, 'hex');
    const signature = Buffer.from(transaction.signature, 'hex');
    if (!secp256k1.ecdsaVerify(signature, crypto.createHash('sha256').update(message).digest(), publicKey)) {
        return false;
    }

    return true;
}

// Function to process a single transaction file
function processTransactionFile(filePath) {
    try {
        // Read transaction data from file
        const transactionData = fs.readFileSync(filePath, 'utf8');
        const transaction = JSON.parse(transactionData);
        
        // Check if transaction is valid
        if (isValidTransaction(transaction)) {
            return transaction;
        } else {
            console.log(`Invalid transaction: ${filePath}`);
            return null;
        }
    } catch (error) {
        console.error(`Error processing file ${filePath}: ${error.message}`);
        return null;
    }
}

// Function to process all transaction files in the mempool folder
function processAllTransactions(folderPath) {
    const validTransactions = [];
    try {
        // Read all files in the folder
        const files = fs.readdirSync(folderPath);
        
        // Process each file
        files.forEach(file => {
            const filePath = `${folderPath}/${file}`;
            const transaction = processTransactionFile(filePath);
            if (transaction) {
                validTransactions.push(transaction);
            }
        });
    } catch (error) {
        console.error(`Error reading folder ${folderPath}: ${error.message}`);
    }
    return validTransactions;
}

// Function to mine a block
function mineBlock(transactions) {
    // Generate coinbase transaction
    const coinbaseTransaction = {
        id: 'coinbase_transaction_id',
        // Other coinbase transaction data can be added here
    };

    // Serialize coinbase transaction
    const serializedCoinbaseTransaction = JSON.stringify(coinbaseTransaction);

    // Serialize transactions
    const serializedTransactions = transactions.map(tx => tx.id).join('\n');

    // Create block header (for demonstration purposes, a simple hash of concatenated data is used)
    const blockHeader = crypto.createHash('sha256').update(serializedCoinbaseTransaction + serializedTransactions).digest('hex');

    // Write data to output.txt
    fs.writeFileSync('output.txt', `${blockHeader}\n${serializedCoinbaseTransaction}\n${serializedTransactions}`);

    console.log('Block mined successfully!');
}

// Specify the path to the mempool folder
const mempoolFolderPath = './mempool';

// Process all transactions in the mempool folder
const validTransactions = processAllTransactions(mempoolFolderPath);

// Mine block using valid transactions
mineBlock(validTransactions);
