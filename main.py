import streamlit as st
from st_pages import Page, show_pages, add_page_title

def main():
    st.set_page_config(page_title="WillemGPT🍺", page_icon=":beer_mug:")

    st.title("WillemGPT🍺")  # Algemene titel bovenaan elke pagina

    with st.sidebar:
        st.title("Menu")  # Titel voor de menubalk

    show_pages(
        [
            Page("Documenten_chat.py", "Chat met je PDFs OpenAI", "📎"),
            Page("Text_to_Image.py", "Text to Image", "🖼️"),
            Page("Documenten_chat_lokaal.py", "Chat met je PDFs lokaal", "📎"),
            Page("Instellingen.py", "Instellingen", "⚙️")
        ]
    )

    add_page_title()  # Optioneel

if __name__ == '__main__':
    main()
