from core.storage import DeckStorage

storage = DeckStorage("data/deck.json")
print(f"Zaladowany {len(storage.cards)} kart")

due_cards = storage.get_due()
print(f"do powtorki {len(due_cards)}")

for card in due_cards:
    print(f"- {card['id']}: {card['front']} (due_at={card['due_at']})")
