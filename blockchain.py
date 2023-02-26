import datetime
import json
import hashlib
from flask import Flask, jsonify

class Blockchain:

    def __init__(self):
        # เก็บกลุ่มของ Block
        self.chain = []  # list ที่เก็บ Block
        self.transaction = ""
        # genesis block
        self.create_block(nonce=1, previous_hash="0")

    # สร้าง Block ขึ้นมาในระบบ Blockchain
    def create_block(self, nonce, previous_hash):
        # เก็บส่วนประกอบของ Block แต่ละ Block
        block = {
            "index": len(self.chain)+1,
            "timestamp": str(datetime.datetime.now()),
            "nonce": nonce,
            "data": self.transaction,
            "previous_hash": previous_hash
        }
        self.chain.append(block)
        return block

    # ให้บริการเกี่ยวกับ Block ก่อนหน้า
    def get_previous_block(self):
        return self.chain[-1]

    # เข้ารหัส Block
    def hash(self, block):
        # แปลง Python object (dict) => json object
        encode_block = json.dumps(block, sort_keys=True).encode()
        # sha-256
        return hashlib.sha256(encode_block).hexdigest()

    # find nonce
    def proof_of_work(self, previous_nonce):
        # อยากได้ค่า nonce = ??? ที่ส่งผลให้ได้ target hash => 4 หลักแรก => 0000XXXXXXXXX
        new_nonce = 1  # ค่า nonce ที่ต้องการ
        check_proof = False   # ตัวแปรที่ check ค่า nonce ให้ได้ตาม target ที่กำหนด

        # แก้โจทย์ทางคณิตศาสตร์
        while check_proof is False:
            # เลขฐาน 16 มา 1 ชุด
            hashoperation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hashoperation[:4] == "0000":
                check_proof = True
            else:
                new_nonce += 1
        return new_nonce
    
    # ตรวจสอบ Block
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        while block_index<len(chain):
            block = chain[block_index] #block ที่ตรวจสอบ
            
            # ตรวจสอบ hash of block
            if block["previous_hash"] != self.hash(previous_block):
                return False
            
            # ตรวจสอบ nonce ที่ทำให้ hashoperation to target
            previous_nonce = previous_block["nonce"] # nonce block ก่อนหน้า
            nonce = block["nonce"] # nonce ของ block ที่ตรวจสอบ
            hashoperation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hashoperation[:4] != "0000":
                return False
            
            # ตรวจสอบ block ถัดไป
            previous_block = block
            block_index +=1
        return True

# web server
app = Flask(__name__)
# ใช้งาน Block
blockchain = Blockchain()

# routing
@app.route('/')
def hello():
    return "<h1>Hello Blockchain</h1>"
@app.route('/get_chain', methods=["GET"])
def get_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200
@app.route('/mining', methods=["GET"])
def mining_block():
    
    # add transaction
    transaction =  "นาย A ส่ง 100 bitcoin ให้นาย B,"
    blockchain.transaction = transaction
    
    # ตัวแปรที่ใช้ใน method นี้
    previous_block = blockchain.get_previous_block()
    previous_nonce = previous_block["nonce"]
    # find nonce
    nonce = blockchain.proof_of_work(previous_nonce)
    # hash block ก่อนหน้า
    previous_hash = blockchain.hash(previous_block)
    # update block ใหม่
    block = blockchain.create_block(nonce, previous_hash)
    response = {
        "message": "Mining Block เรียบร้อย",
        "index": block["index"],
        "timestamp": block["timestamp"],
        "data": block["data"],
        "nonce": block["nonce"],
        "previous_hash": block["previous_hash"]
    }
    return jsonify(response),200
@app.route('/is_valid', methods=["GET"])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response={"message": "Blockchain Is Valid"}
    else:
        response={"message": "Have Problem , Blockchain Is Not Valid"}
    return jsonify(response),200            

# run server
if __name__ == "__main__":
    app.run()
