import streamlit as st
from collections import Counter

# Step 1: Define values for cards like J, Q, K, A
CARD_NUMBERS = {
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12,
    'K': 13, 'A': 14
}

# Step 2: Define the order of poker hands
HAND_RANKS = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind",
    "Straight", "Flush", "Full House", "Four of a Kind",
    "Straight Flush", "Royal Flush"
]

# Step 3: Convert a card like '10H' into (number, suit)
def parse_card(card_str):
    card_str = card_str.upper().strip()
    if len(card_str) < 2:
        return None
    number_part = card_str[:-1]
    suit_part = card_str[-1]
    if number_part not in CARD_NUMBERS or suit_part not in "HDCS":
        return None
    number = CARD_NUMBERS[number_part]
    return (number, suit_part)

# Step 4: Check if cards form a straight
def is_straight(numbers):
    unique_numbers = list(set(numbers))
    unique_numbers.sort()
    if len(unique_numbers) < 5:
        return False, None
    for i in range(len(unique_numbers) - 4):
        if unique_numbers[i+4] - unique_numbers[i] == 4:
            return True, unique_numbers[i+4]
    if 14 in unique_numbers and all(x in unique_numbers for x in [2, 3, 4, 5]):
        return True, 5
    return False, None

# Step 5: Evaluate hand
def evaluate_hand(cards):
    numbers = [c[0] for c in cards]
    suits = [c[1] for c in cards]
    numbers.sort(reverse=True)
    count_numbers = Counter(numbers)
    all_same_suit = len(set(suits)) == 1
    is_str, high_straight = is_straight(numbers)

    if all_same_suit and set(numbers) == set([10, 11, 12, 13, 14]):
        return (9, [])
    if all_same_suit and is_str:
        return (8, [high_straight])
    for number in count_numbers:
        if count_numbers[number] == 4:
            kicker = max(n for n in numbers if n != number)
            return (7, [number, kicker])

    three_of_kind = [n for n in count_numbers if count_numbers[n] == 3]
    pairs = [n for n in count_numbers if count_numbers[n] == 2]

    if three_of_kind:
        three = max(three_of_kind)
        if pairs:
            return (6, [three, max(pairs)])
        if len(three_of_kind) > 1:
            return (6, [three, min(three_of_kind)])
    if all_same_suit:
        return (5, numbers)
    if is_str:
        return (4, [high_straight])
    if three_of_kind:
        three = max(three_of_kind)
        kickers = [n for n in numbers if n != three][:2]
        return (3, [three] + kickers)
    if len(pairs) >= 2:
        sorted_pairs = sorted(pairs, reverse=True)[:2]
        kicker = max(n for n in numbers if n not in sorted_pairs)
        return (2, sorted_pairs + [kicker])
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = [n for n in numbers if n != pair][:3]
        return (1, [pair] + kickers)
    return (0, numbers[:5])

# Step 6: Compare two hands
def compare_hands(a, b):
    if a[0] != b[0]:
        return a[0] - b[0]
    return (a[1] > b[1]) - (a[1] < b[1])

# Streamlit UI starts
st.set_page_config(page_title="Poker Evaluator", layout="centered")
st.title("🃏 Poker Hand Evaluator")

if "players" not in st.session_state:
    st.session_state.players = [[]]
if "results" not in st.session_state:
    st.session_state.results = [None]
if "last_cards" not in st.session_state:
    st.session_state.last_cards = ["" for _ in range(5)]
if "disable_check" not in st.session_state:
    st.session_state.disable_check = [False]

if st.button("➕ Add Player"):
    st.session_state.players.append([])
    st.session_state.results.append(None)
    st.session_state.disable_check.append(False)

# Re-calculate used cards each run
all_cards_flat = []
for i in range(len(st.session_state.players)):
    row = []
    for j in range(5):
        card = st.session_state.get(f"p{i}_c{j}", "").strip().upper()
        if card:
            row.append(card)
    if len(row) == 5:
        all_cards_flat.extend(row)
used_set = set()
duplicated = False
for card in all_cards_flat:
    if card in used_set:
        duplicated = True
    used_set.add(card)

# Input and check for each player
for i in range(len(st.session_state.players)):
    st.subheader(f"Player {i+1}")
    cols = st.columns(5)
    current_hand = []
    card_changed = False

    for j in range(5):
        key = f"p{i}_c{j}"
        old_value = st.session_state.get(key, "")
        card = cols[j].text_input(f"Card {j+1}", value=old_value, key=key)
        current_hand.append(card)

    parsed = [parse_card(c) for c in current_hand]
    card_ids = [c.upper().strip() for c in current_hand]

    # Re-enable button if any card changed
    if st.session_state.results[i] is not None:
        if any(st.session_state.get(f"p{i}_c{j}", "").strip().upper() != card_ids[j] for j in range(5)):
            st.session_state.results[i] = None
            st.session_state.disable_check[i] = False

    if st.button(f"Check Hand Rank (Player {i+1})", disabled=st.session_state.disable_check[i]):
        if None in parsed:
            st.error(f"Player {i+1}: Invalid card(s).")
        elif len(set(card_ids)) < 5:
            st.error(f"Player {i+1}: Duplicate cards in hand.")
        elif len(set(all_cards_flat)) < len(all_cards_flat):
            st.error(f"Player {i+1}: Duplicate card used by multiple players.")
        else:
            result = evaluate_hand(parsed)
            st.session_state.results[i] = result
            st.session_state.disable_check[i] = True
            st.success(f"Player {i+1} has a {HAND_RANKS[result[0]]}")

# Find winner
if st.button("🏆 Find Winner"):
    if any(r is None for r in st.session_state.results):
        st.warning("Please check all players' hands first.")
    else:
        best = max(st.session_state.results)
        winners = [i+1 for i, r in enumerate(st.session_state.results) if r == best]

        for i, r in enumerate(st.session_state.results):
            st.write(f"Player {i+1}: {HAND_RANKS[r[0]]}")

        if len(winners) == 1:
            st.success(f"🏆 Player {winners[0]} wins with a {HAND_RANKS[best[0]]}!")
        else:
            st.info(f"🤝 It's a tie between players: {', '.join(str(w) for w in winners)}")

# Note: Duplicate card checking is enforced. To allow duplicates (like in testing), remove used_set logic.
