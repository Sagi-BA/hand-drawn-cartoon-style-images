import streamlit as st
from streamlit.components.v1 import html
import os

def initialize():    

    # Load header content
    header_file_path = os.path.join('utils', 'header.md')
    try:
        with open(header_file_path, 'r', encoding='utf-8') as header_file:
            header_content = header_file.read()
    except FileNotFoundError:
        st.error("header.md file not found in utils folder.")
        header_content = ""  # Provide a default empty header

    # Extract title and image path from header content
    header_lines = header_content.split('\n')
    title = header_lines[0].strip('# ')
    image_path = None    
    for line in header_lines:
        if line.startswith('!['):
            image_path = line.split('(')[1].split(')')[0]
            break

    st.set_page_config(layout="wide", page_title=f"{title}", page_icon="🖼️")
    st.title(f"{title}")
    
    # Load external CSS
    css_file_path = os.path.join('utils', 'styles.css')
    with open(css_file_path, 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)    
    
    # Load footer content
    footer_file_path = os.path.join('utils', 'footer.md')
    try:
        with open(footer_file_path, 'r', encoding='utf-8') as footer_file:
            footer_content = footer_file.read()
    except FileNotFoundError:
        st.error("footer.md file not found in utils folder.")
        footer_content = ""  # Provide a default empty footer    

    with st.expander('אודות האפליקציה - נוצרה ע"י שגיא בר און'):
        st.markdown('''
        אפליקציית Streamlit זו מבוססת מודל שפה AI המייצר מילים רנדומאלי ומבצע בדיקות למתן ניקוד.
        
        - הדגם מיומן ביצירת איורים גחמניים ומסוגננים של אנשים, בעלי חיים וסצנות טבע, תוך שמירה על סגנון קלאסי ווינטג'י ייחודי.
        - בהשוואה לדגמים אחרים, כמו BandW-Manga שמייצרת אמנות נועזת בהשראת מנגה בשחור-לבן, דגם זה מציע אסתטיקה רכה ועדינה יותר. התמונות שהוא יוצר נראות כמו מצוירות ביד, עם משיכות מכחול זורחות ופלטת צבעים מושתקת.
        - הדגם מסוגל לתאר מגוון רחב של נושאים, מקטנה השוטטת ביער ועד קרפדה או אמן משרטט. למרות שהתוצאות הן דמיוניות ומקסימות, הדגם עשוי להיתקל בקשיים בהפקת ייצוגים מציאותיים במיוחד של פנים אנושיות וסצנות מורכבות.
        ''')

    return image_path, footer_content