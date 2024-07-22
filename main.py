import streamlit as st
import asyncio
import uuid
import os
import base64
from functools import lru_cache
from PIL import Image
import requests
from langdetect import detect
from deep_translator import GoogleTranslator
from gradio_client import Client

from utils.init import initialize
from utils.counter import initialize_user_count, increment_user_count, get_user_count
from utils.TelegramSender import TelegramSender

# Constants
UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = {
        'telegram_sender': TelegramSender(),
        'counted': False,
        'image_path': None,
        'user_prompt': "",
    }

# Initialize translator
translator = GoogleTranslator(source='auto', target='en')

@lru_cache(maxsize=32)
def get_binary_file_downloader_html(bin_file, file_label='קובץ'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'data:application/octet-stream;base64,{bin_str}'
    return f'<a href="{href}" download="{os.path.basename(bin_file)}" class="download-button">לחיצה להורדת {file_label}</a>'

def get_image_download_link(img_path, filename):
    with open(img_path, "rb") as file:
        st.download_button(
            label="Download Image",
            data=file,
            file_name=filename,
            mime="image/jpeg",
            key=f"download_{uuid.uuid4()}"
        )

def translate_if_hebrew(text):
    try:
        return translator.translate(text) if detect(text) == 'he' else text
    except Exception as e:
        st.warning(f"Translation error: {str(e)}. Proceeding with original text.")
        return text

def cleanup_image():
    if st.session_state.state['image_path'] and os.path.exists(st.session_state.state['image_path']):
        os.remove(st.session_state.state['image_path'])
        st.session_state.state['image_path'] = None

def process_result(result):
    filename = f"generated_image_{uuid.uuid4()}.jpg"
    dest_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if isinstance(result, str):
        if os.path.isfile(result):
            img = Image.open(result)
        elif result.startswith(('http://', 'https://')):
            response = requests.get(result)
            if response.status_code == 200:
                img = Image.open(requests.get(result).content)
            else:
                raise Exception(f"Failed to download image from URL: {result}")
        else:
            raise Exception(f"Invalid result format: {result}")
    elif isinstance(result, Image.Image):
        img = result
    else:
        raise Exception(f"Unexpected result format: {type(result)}")
    
    img = img.convert('RGB')
    img.save(dest_path, 'JPEG')
    return dest_path

def set_prompt(prompt):
    st.session_state.state['user_prompt'] = prompt

async def main():
    image_path, footer_content = initialize()
    
    if image_path:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image_path, use_column_width=True)
        
    example_prompts = [
        "שקיעה יפהפייה על חוף הים",
        "חתול חמוד משחק עם כדור צמר",
        "נוף הררי מושלג בסתיו",
        "עיר עתיקה עם סמטאות צרות",
        "פרפר צבעוני על פרח סגול"
    ]      
    
    st.markdown("### דוגמא להנחיות טקסט:")
    cols = st.columns(5)
    for i, prompt in enumerate(example_prompts):
        cols[i].button(prompt, key=f"example_{i}", on_click=set_prompt, args=(prompt,))

    user_prompt = st.text_area("יש להזין הנחייה ליצירת התמונה:", key="user_prompt", value=st.session_state.state['user_prompt'])
    
    # Add a custom class to the st.text_area
    # st.markdown('<div class="custom-text-area"></div>', unsafe_allow_html=True)
    
    if st.button("לייצר תמונה") and user_prompt:
        cleanup_image()

        with st.spinner("מייצר תמונה נא להמתין בסבלנות..."):
            translated_prompt = translate_if_hebrew(user_prompt)
            
            if translated_prompt != user_prompt:
                st.info(f"תרגום הפרומפט לאנגלית: {translated_prompt}")

            client = Client("fujohnwang/alvdansen-littletinies")
            result = client.predict(translated_prompt, api_name="/predict")
            
            try:
                image_path = process_result(result)
                st.session_state.state['image_path'] = image_path

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(image_path, caption="התמונה שנוצרה", use_column_width=True)
                    st.markdown(get_binary_file_downloader_html(image_path, 'תמונה'), unsafe_allow_html=True)
                
                await send_telegram_message_and_file(f"hand-drawn-cartoon-style-images: {user_prompt}", image_path)

            except Exception as e:
                st.error(f"שגיאה בעיבוד התמונה: {str(e)}")

            finally:
                # Delete the file after sending and displaying
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted temporary file: {image_path}")

    user_count = get_user_count(formatted=True)
    footer_with_count = f"{footer_content}\n\n<p class='user-count' style='color: #4B0082;'>סה\"כ משתמשים: {user_count}</p>"
    st.markdown(footer_with_count, unsafe_allow_html=True)

async def send_telegram_message_and_file(message, file_path):
    sender = st.session_state.telegram_sender
    try:
        await sender.send_document(file_path, message)
    finally:
        await sender.close_session()

if __name__ == "__main__":
    if 'telegram_sender' not in st.session_state:
        st.session_state.telegram_sender = TelegramSender()
    if 'counted' not in st.session_state:
        st.session_state.counted = True
        increment_user_count()
    initialize_user_count()
    asyncio.run(main())