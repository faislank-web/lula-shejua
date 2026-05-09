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
TUJUAN_1 = -1002981455085
TUJUAN_2 = -1003956520342

client = TelegramClient(StringSession(RAW_SESSION.strip()), API_ID, API_HASH, sequential_updates=True)

def proses_teks_custom(teks, tipe_tujuan):
    if not teks: return ""
    # Pembersihan
    teks = re.sub(r'[*_`~\[\]]', '', teks)
    teks = re.sub(r'https?://\S+', '', teks)
    teks = re.sub(r't\.me/\S+', '', teks)
    teks = re.sub(r'@\S+', '', teks)
    
    kamus = {
        "New TV Show Added!": "Series Update",
        "New Movie Added!": "Movie Update",
        "New Episode Released": "Episode Baru Tersedia"
    }
    
    if tipe_tujuan == "tujuan_1":
        kamus["Download Via"] = "silakan Request ke Bunda"
        footer = "\n\n\nby Dhisa @nontonbarengFM"
    else:
        kamus["Download Via"] = "silakan Request ke Admin @anmdni"
        footer = "\n\n\nby Admin @anmpanen138"

    for lama, baru in kamus.items():
        teks = re.sub(re.escape(lama), baru, teks, flags=re.IGNORECASE)
    return teks.strip() + footer

async def main():
    print("--- DHISA & ADMIN: MODE 2 TUJUAN AKTIF --- 🎀")
    try:
        await client.connect()
        if not await client.is_user_authorized(): return
        
        markup_1 = [Button.url("Channel Utama 💎", "https://t.me/nontonbarengFM")]
        markup_2 = [Button.url("Channel Utama 💎", "https://t.me/anmpanen138")]
        
        last_id = 0
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r") as f:
                c = f.read().strip()
                if c: last_id = int(c)

        # Gunakan limit untuk memastikan ada pesan yang diambil jika min_id macet
        async for msg in client.iter_messages(SUMBER, min_id=last_id, limit=None, reverse=True):
            # JANGAN update last_id di sini jika pesan dilewati agar tidak macet
            if msg.action or not msg.media:
                continue
            
            try:
                # Kirim ke Tujuan 1
                cap_1 = proses_teks_custom(msg.text, "tujuan_1") if msg.text else "Update Baru 🎬"
                await client.send_message(TUJUAN_1, cap_1, file=msg.media, buttons=markup_1)
                
                # Kirim ke Tujuan 2
                cap_2 = proses_teks_custom(msg.text, "tujuan_2") if msg.text else "Update Baru 🎬"
                await client.send_message(TUJUAN_2, cap_2, file=msg.media, buttons=markup_2)
                
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
