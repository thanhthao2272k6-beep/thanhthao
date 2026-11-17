
from web3 import Web3

# 1. Connect Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.is_connected():
    raise Exception("Cannot connect to Ganache")

print("Connected:", w3.is_connected())
print("Chain ID:", w3.eth.chain_id)

# 2. Ganache accounts
admin = w3.eth.accounts[0]
applicant1 = w3.eth.accounts[1]
applicant2 = w3.eth.accounts[2]

print("Admin:", admin)
print("Applicant 1:", applicant1)
print("Applicant 2:", applicant2)

# 3. Contract address
contract_address = Web3.to_checksum_address(
    "0x1a77A48f61609f7609FA24da2414F9c50774D1bb"
)

# 4. Contract ABI
abi = [
    {
        "inputs": [{"internalType": "string", "name": "_applicationRef", "type": "string"}],
        "name": "submitApplication",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_applicant", "type": "address"}],
        "name": "acceptApplication",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_applicant", "type": "address"}],
        "name": "rejectApplication",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_applicant", "type": "address"}],
        "name": "getApplication",
        "outputs": [
            {"internalType": "string", "name": "applicationRef", "type": "string"},
            {"internalType": "uint8", "name": "status", "type": "uint8"},
            {"internalType": "uint256", "name": "submittedAt", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# 5. Connect Smart Contract
contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

def send_transaction(tx_hash):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Transaction Hash:", tx_hash.hex())
    print("Transaction Status:", receipt.status)
    print("Gas Used:", receipt.gasUsed)
    return receipt

# 6. Submit application SV002
print("\n--- SUBMIT APPLICATION ---")
tx = contract.functions.submitApplication("SV002").transact({
    "from": applicant1,
    "gas": 500000
})
send_transaction(tx)

# 7. Admin accepts application
print("\n--- ACCEPT APPLICATION ---")
tx = contract.functions.acceptApplication(applicant1).transact({
    "from": admin,
    "gas": 500000
})
send_transaction(tx)

# 8. Submit application SV003
print("\n--- SUBMIT SECOND APPLICATION ---")
tx = contract.functions.submitApplication("SV003").transact({
    "from": applicant2,
    "gas": 500000
})
send_transaction(tx)

# 9. Admin rejects application
print("\n--- REJECT APPLICATION ---")
tx = contract.functions.rejectApplication(applicant2).transact({
    "from": admin,
    "gas": 500000
})
send_transaction(tx)

# 10. Read results
print("\n--- FINAL RESULTS ---")

for applicant in [applicant1, applicant2]:
    result = contract.functions.getApplication(applicant).call()
    print("Applicant:", applicant)
    print("Application Reference:", result[0])
    print("Status:", result[1])
    print("Submitted At:", result[2])
    print("--------------------")
