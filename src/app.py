import streamlit as st
import pandas as pd
import os
import json
import shutil

OCENY_FILE = "oceny.csv"

st.set_page_config(page_title="Ocena rozmów", layout="wide")
st.title("📂 System oceny rozmów z botem")

base_path = '/home/msadowski/hack_ai/hack-ai-prompt-buddies/'

dir_path = base_path + 'logs'
files = [f for f in os.listdir(dir_path) if f.endswith(".json")] if os.path.isdir(dir_path) else []

if not files:
    st.warning("Brak plików JSONL w katalogu.")
else:
    selected_file = st.selectbox("📄 Wybierz plik do oceny", sorted(files))
    file_path = os.path.join(dir_path, selected_file)

    messages = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                messages.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                st.warning("Błąd dekodowania jednej z linii.")

    st.subheader("💬 Rozmowa:")
    for msg in messages:
        if "bot" in msg:
            with st.chat_message("assistant"):
                st.text(msg["bot"])
        elif "user" in msg:
            with st.chat_message("user"):
                st.text(msg["user"])

    st.subheader("✅ Ocena tej rozmowy:")
    ocena = st.radio("Wybierz ocenę:", ["poprawna", "błąd", "niejednoznaczna"])
    uwagi = st.text_area("📝 Opcjonalne uwagi")
    category = st.radio('Wybierz kategorię:', ['Halucyjancje', 'Misklasyfikacja', 'Zbieranie Informacji', 'Zabezpieczenie przed hackowaniem', 'Inne'])

    if os.path.exists(OCENY_FILE):
        df_oceny = pd.read_csv(OCENY_FILE)
    else:
        df_oceny = pd.DataFrame(columns=["file_name", "ocena", "uwagi"])

    if st.button("💾 Zapisz ocenę"):
        df_oceny = df_oceny[df_oceny["file_name"] != selected_file]
        new_row = pd.DataFrame([{
            "file_name": selected_file,
            "ocena": ocena,
            "kategoria": category,
            "uwagi": uwagi
        }])
        df_oceny = pd.concat([df_oceny, new_row], ignore_index=True)
        df_oceny.to_csv(OCENY_FILE, index=False)
        
        rated_dir = base_path + 'logs_rated'
        os.makedirs(rated_dir, exist_ok=True)

        src = os.path.join(dir_path, selected_file)
        dst = os.path.join(rated_dir, selected_file)

        try:
            shutil.move(src, dst)
            st.success(f"Ocena zapisana i plik przeniesiony do: {rated_dir}")
        except Exception as e:
            st.error(f"Nie udało się przenieść pliku: {e}")


    st.rerun()