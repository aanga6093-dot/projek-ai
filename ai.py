import requests
import json
import time
import re
import os
from datetime import datetime

class Gemini:
    def __init__(self, file_riwayat,prompt, model):
        self.suara_bicara = True
        self.file_riwayat = file_riwayat
        self.model = model
        self.prompt = [{"parts":[{"text":prompt}]}]
        self.api_key = ""

        self.url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.api_key}"
        )

        self.headers = {"Content-Type": "application/json"}
        self.chat_history = self.prompt + self.get_riwayat_penting()
        
        #ambil jika data chat pausan ada 
        if os.system("cat state.json") not in ["[]",""]:
            with open("state.json","r") as f:
                self.percakapan_sekarang = [json.load(f)]
                
    def minta_respone_ai(self,payload):
        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload
        )

        if response.status_code == 429:
            print("limit kena tunggu 60 detik lagi")
            time.sleep(60)
            returp
        elif response.status_code == 200:
            data = response.json()
            text_ai = data["candidates"][0]["content"]["parts"][0]["text"]
            return text_ai
        else:
            print("status code",response.status_code)
            comit = []
            
    def get_riwayat_penting(self):
        try:
            with open(self.file_riwayat, "r") as file:
                return json.load(file)[1:]
        except FileNotFoundError:
            return []
            
    def save_riwayat_penting(self):
        prompt_comit = """
-ringkas apa saja yanh telan di lakukan di termux
-ringas singkat seperlu dan sepentingnya seperti meng isi projek memori
-ringkas minimal 10 beris
-jangan menjelaskan proses berfikir
-Jangan menulis command yang sudah jelas dari history terminal kecuali penting.

contoh:

*  main.py berjalan di latar belkang memprint halo ke log.txt 
*  Menginstal `vim`.
*  Menginstal `git`.
*  Menghapus `vim`.
*  Menghapus `git`.
        """
        
        payload_comit = {
            "contents": self.prompt + self.percakapan_sekarang + [{
                "role":"user",
                "parts":[{"text":prompt_comit}]
            }]
        }
        
        comit = [{
                "role":"model",
                "parts":
                [{"text":self.minta_respone_ai(payload_comit)}]
            }]
        #simpen comitan ai bentuk json      
        with open(self.file_riwayat, "w") as file:
            json.dump(self.chat_history + comit, file, indent=2)
            
    # Jalankan bash / python / dan ngomong
    def eksekusi_perintah(self, text):
        ada_bash = re.search(r"```bash\s*(.*?)\s*```\s*(.*)",text,re.S)
        ada_python = re.search(r"```bash\s*(.*?)\s*```\s*(.*)",text,re.S)
        
        if ada_bash:
            code_bash = ada_bash.group(1)
            text_ai = ada_bash.group(2)
            os.system(code_bash)
        elif ada_python:
            code_python = ada_python.group(1)
            text_ai = ada_python.group(2)
            exec(code_python)
        else:
            text_ai = ""
            
        if self.suara_bicara:
            os.system("termux-tts-speak " + text_ai)
            
    # Kirim prompt ke Gemini
    def kirim(self, user_input):

        self.percakapan_sekarang.append({
            "role": "user",
            "parts": [{"text": user_input}]
        })

        payload = {
            "contents": self.chat_history + self.percakapan_sekarang
        }
        
        text_ai = self.minta_respone_ai(payload)
        print("\n\033[34mresponse AI:\n")
        print(text_ai)

        self.eksekusi_perintah(text_ai)

        self.percakapan_sekarang.append({
            "role": "model",
            "parts": [{"text": text_ai}]
            })
                    
    # Loop chat
    def run(self):
        
        while True:
            user_input = input("\033[32mprompt<<").lower()
            print()
            if user_input in ["exit", "quit"] or ():
                self.save_riwayat_penting()
                os.system("echo '[]' > state.json") #hapus isi data satate.json
                break
            elif user_input == "pause":
                #simpen dulu chat sekarang 
                with open("state.json","w") as f:
                    json.dump(self.percakapan_sekarang[1:],f,indent=2)
                break
                
            self.kirim(user_input)


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
    model="gemini-2.5-flash"
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
    model="gemini-2.5-flash-lite"
)

gemini_lite.run()
    
