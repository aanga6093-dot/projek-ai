import requests
import json
import re
import os

API_KEY = "--API-KEY--"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

try:
    with open("memori.txt","r") as r:
        memori = r.read()
    print(memori)
except FileNotFoundError:
    print("membuat file memori")
    with open("memori.txt","a") as f:
        f.write("user suka coding"+"\n")
            
chat = {
    "contents": [{"parts":[{
        "text":f"""
**kontex**
    -anda ai api yang di buat saya di dalam python 
    
**aturan**
    -berbicara dengan singkat gaya obrol Sunda singkat 
    
**memori**
    -user suka main 
{memori}
"""+"""  
**tols**
    -simpan data yang menurut anda penting di percakapan ke memori dengan cara ketik ```json [{"mode":"add","data":<DATA YANG INGIN DI TAMBAHAHKAN>}] ```
    contoh:  ```json [{"mode":"add","data": "-user suka nyoli"}] ```
"""
        }]}]
}

headers = {
    "Content-Type": "application/json"
}

while True:
    prompt = input("\nyou:")
    if prompt in ["exit"]:
        break
    
    chat["contents"].append({
        "role":"user",
        "parts":[{"text":prompt}]
    })
    response = requests.post(url, headers=headers, json=chat)

    if response.status_code == 200:
        data = response.json()

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print("\n=== RESPON GEMINI ")
            print(text)
            chat["contents"].append({
                "role":"model",
                "parts":[{"text":text}]
                
            })
            
            ada_json = re.search(r"```bash\s*(.*?)\s*```", text, re.S)
            if ada_json:
                data_add = json.load(ada_json.group(1))[0]["data"]
                memori += "    " + data_add + "\n"
                with open("memori.txt","a") as var:
                    # TODO: write code...
                    var.write(data_add + "\n")
        except Exception:
            print("Format respons tidak dikenali")
            print(json.dumps(data, indent=2))

    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
