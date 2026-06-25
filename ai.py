import requests
import json
import time
import re
import os
import asyncio

#halo bang 


class Gemini:

    def __init__(self, file_riwayat,prompt, model, api_key):
        
        self.file_riwayat = file_riwayat
        self.model = model
        self.api_key = api_key

        self.json_prompt = [{"parts":[{"text":prompt}]}]
        self.url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )

        self.headers = {
            "Content-Type": "application/json"
        }
        self.chat_now = []
        self.chat_history = self.json_prompt.copy()
        self.chat_history.extend(self.get_riwayat()[1:])
        

    # Ambil riwayat chat
    def get_riwayat(self):
        try:
            with open(self.file_riwayat, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    # Simpan riwayat
    def save_riwayat(self):
        prompt_comit = """
-ringkas apa saja yanh telan di lakukan di termux
-ringas singkat seperlu dan sepentingnya seperti meng isi projek memori
-ringkas minimal 10 beris
-jangan menjelaskan proses berfikir
-Jangan menulis command yang sudah jelas dari history terminal kecuali penting.

contoh:

Berikut adalah ringkasan singkat aktivitas yang telah dilakukan di Termux:

*   Menginstal `vim`.
*   Menginstal `git`.
*   Menghapus `vim`.
*   Menghapus `git`.


        """
        payload_comit = {
            "contents": self.json_prompt + self.chat_now + [{
                "role":"user",
                "parts":[{"text":prompt_comit}]
            }]
        }
        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload_comit
        )

        if response.status_code == 429:
            print("limit kena tunggu 60 detik lagi")
            time.sleep(60)
            return

        elif response.status_code == 200:

            data = response.json()
            

            try:
                text= data["candidates"][0]["content"]["parts"][0]["text"]
                comit = [{
                    "role":"model",
                    "parts":
                    [{"text":text}]
                }]
                print(text)
            except Exception:
                print("Format error")
                comit = []
                
        else:
            print("status code",response.status_code)
            comit = []
        with open(self.file_riwayat, "w") as file:
            json.dump(self.chat_history+comit, file, indent=2)
            
    def bot_spak(self,text):
        ada_bash = re.search(r"```bash\s*(.*?)\s*```", text, re.S)
        ada_python = re.search(r"```python\s*(.*?)\s*```", text, re.S)

        if ada_bash:
            sript = ada_bash.group(0)
            
        elif ada_python:
            sript = ada_python.group(0)
            
        kata = text.replace(sript,"")
        
        os.system(f"""termux-tts-speak "{kata}" """")
        
            
    # Jalankan bash / python
    def execute_code(self, text):

        ada_bash = re.search(r"```bash\s*(.*?)\s*```", text, re.S)
        ada_python = re.search(r"```python\s*(.*?)\s*```", text, re.S)

        if ada_bash:
            bash = ada_bash.group(1)
            print("\033[49m meng execute...")
            os.system(bash)
            
        elif ada_python:
            code = ada_python.group(1)

            lanjut = input("run y/n : ")
            if lanjut.lower() == "y":
                
                print("\033[49m meng execute...")
                exec(code)
        else:
            print("bash gak di temukan")
    # Kirim prompt ke Gemini
    def kirim(self, user_input):

        self.chat_now.append({
            "role": "user",
            "parts": [{"text": user_input}]
        })

        payload = {
            "contents": self.chat_history + self.chat_now
        }

        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload
        )

        if response.status_code == 429:
            print("limit kena tunggu 60 detik lagi")
            time.sleep(60)
            return

        elif response.status_code == 200:

            data = response.json()

            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]

                print("\n\033[34mresponse AI:\n")
                print(text)

                self.execute_code(text)

                self.chat_now.append({
                    "role": "model",
                    "parts": [{"text": text}]
                })

            except Exception:
                print("Format error")
                print(json.dumps(data, indent=2))

        else:
            print("Error:", response.status_code)
            print(response.text)

    # Loop chat
    def run(self):

        while True:

            user_input = input("\033[32mprompt<< ")
            print()

            if user_input.lower() in ["exit", "quit"]:
                break

            self.kirim(user_input)

        self.save_riwayat()
gemini_flask = Gemini(
    file_riwayat="chat.json",
    prompt= """
peran:
-Kamu ai genedator bash termux
-membuat bash ukuran sedang yang aman
-kamu mengubah input peritah user jadi bash

kontext:
-kamu ai api yang gw buat di pyyhon termux
-saya sudah install termux-api, python
-kamu memiliki akses ke bash termux setiap bash 
yang kamu hasilkan akan di eksekusi

tujuan:
-memudahkan user mengunakan termux tanpa hafal
seluruh bash 
-membuat user langsung meng exsekusi bash langsung
tanpa coppy paste
 
larangan:
-jangan buat perintah bash berbahaya 
-jangan hasilkan bash atau sript yabh ter pisah pisah di keluaran
-jangan bertinfak melebihi asisten user

keluaran:
-posisikan bash di awal lalu penjelasan 
singkat dan konvirmasi di bawah
""",
    model="gemini-2.5-flash",
    api_key=""
)



gemini_lite = Gemini(
    file_riwayat="chat.json",
    prompt= """
peran:
-Kamu ai genedator bash termux
-membuat bash sederhan simpel praktis aman
-kamu mengubah input peritah user jadi bash

kontext:
-kamu ai api yang gw buat di pyyhon termux
-saya sudah install termux-api, python
-kamu memiliki akses ke bash termux setiap bash 
yang kamu hasilkan akan di eksekusi

tujuan:
-memudahkan user mengunakan termux tanpa hafal
seluruh bash 
-membuat user langsung meng exsekusi bash langsung
tanpa coppy paste
 
larangan:
-jangan buat perintah bash berbahaya 
-jangan hasilkan bash atau sript yabh ter pisah pisah di keluaran
-jangan bertinfak melebihi asisten user

keluaran:
-posisikan bash di awal lalu penjelasan 
singkat dan konvirmasi di bawah
""",
    model="gemini-2.5-flash-lite",
    api_key="--API-KEY--"
)

gemini_lite.run()
