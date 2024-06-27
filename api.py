# test_api.py
import requests

stop = False

while stop == False:
    print(" ")
    question = str(input("Enter your question: "))
    if question == "q":
        stop = True
        break


    response = requests.post("http://localhost:5000/ask", json={"question": f"{question}"})
    print("""


    """)
    print(response.json()["response"].split("</s>")[-1].strip())

    print("""


    """)
