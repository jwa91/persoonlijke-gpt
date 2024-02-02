import streamlit as st
from st_pages import Page, show_pages, add_page_title

def main():
    st.set_page_config(page_title="WillemGPT🍺", page_icon=":beer_mug:")

    st.title("WillemGPT🍺")  # Algemene titel bovenaan elke pagina

    show_pages(
        [
            Page("Documenten_chat.py", "Chat met je PDFs", "📎"),
            Page("Text_to_Image.py", "Text to Image", "🖼️"),
            Page("dailyemailcast.py", "Maak een podcast van je ongelezen mail", "🎧"),
            Page("Instellingen.py", "Instellingen", "⚙️")
        ]
    )

    add_page_title()  # Optioneel

if __name__ == '__main__':
    main()
