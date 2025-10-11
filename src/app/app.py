import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import streamlit as st
from datetime import datetime, timezone, timedelta

from core.storage import DeckStorage
from core.srs import update_card_state

DECK_PATH = "data/deck.json"  

st.set_page_config(page_title="Flashcards", page_icon="🧠", layout="centered")
st.title("Flashcards")

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

try:
    storage = DeckStorage(DECK_PATH)
    due_cards = storage.get_due()
except Exception as e:
    st.error(f"Nie udało się wczytać talii: {e}")
    st.stop()

with st.sidebar.expander("➕ Dodaj nową kartę"):
    with st.form("add_card_form", clear_on_submit=False):
        new_front = st.text_area("Front (pytanie)", height=80)
        new_back = st.text_area("Back (odpowiedź)", height=80)
        first_in_days = st.number_input("Pierwsza powtórka za (dni)", min_value=0, max_value=30, value=0, step=1)
        submitted = st.form_submit_button("Dodaj")

        if submitted:
            f = (new_front or "").strip()
            b = (new_back or "").strip()
            if not f or not b:
                st.warning("Front i Back nie mogą być puste.")
            else:
                new_id = (max((c["id"] for c in storage.cards), default=0) + 1)

                first_due = datetime.now(timezone.utc) + timedelta(days=int(first_in_days))

                new_card = {
                    "id": new_id,
                    "front": f,
                    "back": b,
                    "ease": 2.5,
                    "interval": 0,
                    "repetitions": 0,
                    "due_at": DeckStorage.to_iso(first_due),
                }
                storage.cards.append(new_card)
                storage.save()
                st.success(f" Dodano kartę #{new_id}")
                st.rerun()
st.sidebar.metric("Do powtórki dziś", len(due_cards))
st.sidebar.metric("Wszystkich kart", len(storage.cards))
if not due_cards:
    st.success("🎉 Brak kart do powtórki na teraz.")
    st.stop()

card = due_cards[0] 

st.subheader(f"Karta #{card['id']}")
st.write("**Pytanie:**")
st.info(card["front"])

if not st.session_state.show_answer:
    if st.button("Pokaż odpowiedź"):
        st.session_state.show_answer = True
        st.rerun()
else:
    st.write("**Odpowiedź:**")
    st.success(card["back"])

    st.divider()
    st.caption("Oceń od 0 (nie pamiętam) do 5 (bardzo łatwe):")

    def on_grade(grade):
        new_ease, new_interval, new_reps = update_card_state(
            card["ease"], card["interval"], card["repetitions"], grade
        )
        card["ease"] = new_ease
        card["interval"] = int(new_interval)
        card["repetitions"] = int(new_reps)
        next_due = datetime.now(timezone.utc) + timedelta(days=int(new_interval))
        card["due_at"] = DeckStorage.to_iso(next_due)

        try:
            storage.save()
        except Exception as e:
            st.error(f"Nie udało się zapisać zmian: {e}")
            return

        st.session_state.show_answer = False
        st.rerun()

    cols = st.columns(6)
    for g in range(6):
        with cols[g]:
            st.button(str(g), key=f"grade_{g}", on_click=on_grade, args=(g,))

with st.sidebar.expander("Szczegóły bieżącej karty"):
    st.write(
        {
            "ease": card["ease"],
            "interval": card["interval"],
            "repetitions": card["repetitions"],
            "due_at": card["due_at"],
        }
    )
