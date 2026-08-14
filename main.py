import os
import io
import zipfile
import telebot
from PIL import Image
import google.generativeai as genai

# Anahtarlar
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

PROMPT = "Sen Türkçe manga çevirmenisin. Görseldeki İngilizce konuşma balonlarını sırayla doğal, akıcı ve günlük bir Türkçeye çevir. Sadece çevirileri yaz."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Selam! Bana manga sayfası (fotoğraf) veya ZIP dosyası at, Türkçeye çevireyim.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⏳ Çevriliyor...")
    file_info = bot.get_file(message.photo[-1].file_id)
    file_data = bot.download_file(file_info.file_path)
    
    img = Image.open(io.BytesIO(file_data))
    res = model.generate_content([PROMPT, img])
    bot.reply_to(message, f"📖 Çeviri:\n\n{res.text}")

@bot.message_handler(content_types=['document'])
def handle_doc(message):
    if message.document.file_name.lower().endswith('.zip'):
        bot.reply_to(message, "📦 ZIP açılıyor ve sayfalar çevriliyor...")
        file_info = bot.get_file(message.document.file_id)
        file_data = bot.download_file(file_info.file_path)
        
        with zipfile.ZipFile(io.BytesIO(file_data)) as z:
            resimler = sorted([f for f in z.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
            for idx, r in enumerate(resimler, 1):
                try:
                    img = Image.open(io.BytesIO(z.read(r)))
                    res = model.generate_content([PROMPT, img])
                    bot.send_message(message.chat.id, f"📄 Sayfa {idx}:\n\n{res.text}")
                except:
                    pass
        bot.reply_to(message, "✅ Bitti!")

bot.infinity_polling()

