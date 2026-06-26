import asyncio
import os
import re
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# --- DATA DARI GITHUB SECRETS ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
RAW_SESSION = os.environ.get("SESSION_STRING")

SUMBER = -1002186281759
TUJUAN_1 = -1003839747899

client = TelegramClient(StringSession(RAW_SESSION.strip()), API_ID, API_HASH, sequential_updates=True)

def proses_teks_custom(teks):
    if not teks: return ""
    
    # Hapus tanda kurung apa pun sebelum judul agar rapi (misal: [DL NIME])
    teks = re.sub(r'^\[[^\]]+\]\s*', '', teks)
    
    # Pembersihan link lama dan karakter markdown mentah agar tidak tabrakan
    teks = re.sub(r'https?://\S+', '', teks)
    teks = re.sub(r't\.me/\S+', '', teks)
    teks = re.sub(r'@\S+', '', teks)
    teks = re.sub(r'[_`~]', '', teks)  # Menyisakan [] untuk keperluan tautan markdown nanti
    
    kamus = {
        "New TV Show Added!": "Series Update",
        "New Movie Added!": "Sudah Ditambahkan di Channel Movie",
        "New Episode Released": "Episode Baru Tersedia"
    }
    
    for lama, baru in kamus.items():
        teks = re.sub(re.escape(lama), baru, teks, flags=re.IGNORECASE)
        
    # Mengubah Download Via menjadi tautan yang bisa diklik (Markdown style)
    teks = re.sub(r'Download Via', 'Untuk Request [DISINI](https://t.me/+1UMfX90JEZ85MzI1)', teks, flags=re.IGNORECASE)
    
    footer = "\n\nSELAMAT MENYAKSIKAN"
    return teks.strip() + footer

async def main():
    print("--- DHISA & ADMIN: MODE 1 TUJUAN AKTIF --- 🎀")
    try:
        await client.connect()
        if not await client.is_user_authorized(): return
        
        markup_1 = [Button.url("Channel Utama 💎", "https://t.me/shejua")]
        
        last_id = 0
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r") as f:
                c = f.read().strip()
                if c: last_id = int(c)

        async for msg in client.iter_messages(SUMBER, min_id=last_id, limit=None, reverse=True):
            if msg.action or not msg.media:
                continue
            
            # --- FILTER: Melewati postingan New Episode Released ATAU New TV Show Added ---
            if msg.text and (re.search(r'New Episode Released', msg.text, re.IGNORECASE) or 
                             re.search(r'New TV Show Added', msg.text, re.IGNORECASE)):
                print(f"⏭ Melewati ID {msg.id} (Filter detected)")
                
                # Update last_id agar tidak memproses ulang pesan ini di masa depan
                last_id = msg.id
                with open("last_id.txt", "w") as f: f.write(str(last_id))
                continue
            
            try:
                # Kirim ke Tujuan 1 menggunakan parse_mode='md' agar tautan DISINI aktif
                cap_1 = proses_teks_custom(msg.text) if msg.text else "Update Baru 🎬"
                await client.send_message(TUJUAN_1, cap_1, file=msg.media, buttons=markup_1, parse_mode='md')
                
                # Update ID hanya jika BERHASIL kirim media
                last_id = msg.id
                with open("last_id.txt", "w") as f: f.write(str(last_id))
                
                print(f"✅ Berhasil Forward ID: {msg.id}")
                await asyncio.sleep(5) 
                
            except Exception as e:
                print(f"⚠️ Gagal di ID {msg.id}: {e}")
                
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
