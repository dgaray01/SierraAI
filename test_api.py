import requests
from dotenv import load_dotenv
import os

load_dotenv()
server_token = os.getenv('SERVERTOKEN')
print(server_token)
# Check if server_token is None or empty
if not server_token:
    raise ValueError('SERVERTOKEN is not set in the .env file')

headers = {
    'Authorization': f'Bearer {server_token}',
    'Content-Type': 'application/json'
}

stop = False

while not stop:
    print(" ")
    question = input("Enter your question: ")
    if question == "q":
        stop = True
        break

    response = requests.post("http://localhost:5000/api/ask", json={"question": question}, headers=headers)
    print("\n\n")
    print(response.json()["response"].split("</s>")[-1].strip())
    print("\n\n")
