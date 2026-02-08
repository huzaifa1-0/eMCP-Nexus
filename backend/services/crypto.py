from web3 import Web3
from fastapi import HTTPException
from backend.config import settings 
import logging


w3 = Web3(Web3.HTTPProvider(settings.WEB3_RPC_URL))

def verify_payment(tx_hash: str, required_amount: float, receiver_address: str):
    try:
        
        tx = w3.eth.get_transaction(tx_hash)
        
        
        receipt = w3.eth.get_transaction_receipt(tx_hash)

        
        if receipt['status'] != 1:
            raise Exception("Transaction failed on-chain")

        
        if tx['to'].lower() != receiver_address.lower():
            raise Exception("Payment sent to wrong address")

        
        value_in_eth = float(w3.from_wei(tx['value'], 'ether'))
        
        
        if value_in_eth < required_amount:
            raise Exception(f"Insufficient amount. Paid {value_in_eth}, required {required_amount}")

        return True

    except Exception as e:
        logging.error(f"Payment Verification Failed: {e}")
        return False