# module 2-creating Cryptocurrency

#importing the libraries
# request == 2.18.4: pip install requests==2.18.4
import datetime
import hashlib
import json
from flask import Flask, jsonify , request
import requests 
from uuid import uuid4
from urllib.parse import urlparse

# part 1- building a blockchain 

class Blockchain:
    
    def __init__(self):
        #creating empty array to store blocks
        self.chain = []         
        #creating empty list where transaction has to be stored before the block is mined(which has to store these transactions)
        self.transactions = []  
        #creating 1st block of blockchain called "Genesis Block"
        self.create_block(proof=1,previous_hash = '0')  
        #remember we are creating empty set not empty list
        self.nodes = set() #It consist of set of url of all the nodes present in blockchain
         
    def create_block(self,proof,previous_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof, 
                 'previous_hash': previous_hash,
                 'transactions': self.transactions #all Transactions get added to the block when the block is mined
                  }
        self.transactions = [] #after transactions are added to the block,transactions list is made empty to add new set of transactions
        self.chain.append(block)
        return block
        
    def get_previous_block(self):
        return self.chain[-1]  #to return the last block of list

    def proof_of_work(self,previous_proof):
        new_proof =1 
        check_proof =False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof +=1
        return new_proof
    
    def hash(self,block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index =1 
        while block_index < len(chain):
            block =chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                 return False
            previous_block = block
            block_index +=1
        return True
    
    def add_transactions(self, sender, receiver,amount):
        
        #adding transactions to the transaction list
        self.transaction.append({'sender':sender,
                                 'receiver': receiver,
                                 'amount': amount})
        previous_block = self.get_previous_block()
        
        #returning the index of the block which will be mined next and transactions has to be added in that block
        return previous_block['index']+1
    
    def add_node(self,address): #adding new node in blockchain system
        #getting address of the node 
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) # adding the url of node- note we cannot use append method here as it is set not list
    
    def replace_chain(self):  #this function replaces the node having short chain length with the node having greater chain length
        network = self.nodes  
        longest_chain = None
        max_length = len(self.chain)
        for node in network:   # this for loop finds the node having greatest chain length
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length =response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
    # Part 2 - mining our Blockchain 
    # creating a web app
    
app = Flask(__name__)
            
#creating an address for the node on port 5000
node_address = str(uuid4()).replace('-','')  
# uui4() help in creating randomly generated code which act as a address for node on that particular port
# different nodes will have different port and hence different node_address will be created for them


# Creating a Blockchain
    
blockchain = Blockchain()
    
   # Mining  new block
@app.route('/mine_block', methods = ['GET'])
def min_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    blockchain.add_transaction(sender = node_address , receiver = 'you',amount = 1) #adding the transaction to the object blockchain that we created
                                                                                        #before adding other general transactions - first transaction will be amount transfer from node to the miner who mined that block
    block = blockchain.create_block(proof,previous_hash)
    response = {'message': 'comgratulations,you just mined a block',
                'index': block['index'],
                'timestamp':block['timestamp'],
                'proof' : block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions':block['transactions']}
    return jsonify(response), 200
   
   
   # getting full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
        response = {'chain': blockchain.chain,
                    'length': len(blockchain.chain)}
        return jsonify(response), 200

#checking if the blockchain is valid 
@app.route('/is_valid',methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'all good. the blockchain is valid'}
    else:
        response = {'message':'houston,we have a problem. The Blockchain is not valid'}
    return jsonify(response), 200


#adding new transaction to blockchain - through posting json file in postman
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json= request.get_json()
    transaction_keys =['sender','receiver','amount'] #transaction added by the user in postman must have these three keys
    if not all (key in json for key in transaction_keys ): #checking if all three keys are provided by user
        return 'some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount']) #returning the index of the block where transaction has to be stored
    #add_transactions function add the transactions entered by the user into a list called transactions 
    #and that list in turn get added to the block whose index is returned in above line
    
    response = {'message': f'this transaction will be added to block {index}'}
    return jsonify(response), 201


# Connecting new nodes 
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()   # Json= { "node" : ['http//127.0.0.1:5001','http//127.0.0.1:5002','http//127.0.0.1:5003'] - this is the type of json entered by user in postman consisting of node addresses of all the nodes
    nodes= json.get('nodes')    # nodes =  ['http//127.0.0.1:5001','http//127.0.0.1:5002','http//127.0.0.1:5003']
    if nodes is None:
        return "No node",400
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message': 'all nodes are noe connected. The badcoin blockchain now contains the ','total_nodes': list(blockchain.nodes)}
    return jsonify(response),201
    

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain',methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()  # returns true or false depeding upon chain is replaced or not
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced y the largest chain',
                    'new_chain': blockchain.chain}
    else:
        response = {'message':'All good, the chain is the largest chain',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200    


    # Running the app
app.run(host = '0.0.0.0' , port = 5003)
   
    
    
    
#Part 3 - Decentralizing blockchain
    
    
    
    
    
    
    
    
    
    
    
    
    