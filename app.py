import streamlit as st
from collections import Counter

# Mapping from card string to number
CARD_NUMBERS = {
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12,
    'K': 13, 'A': 14
}

HAND_RANKS = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind",
    "Straight", "Flush", "Full House", "Four of a Kind",
    "Straight Flush", "Royal Flush"
]

# Parse card like '10H' to (10, 'H')
def parse_card(card_str):
    card_str = card_str.upper().strip()
    if len(card_str) < 2:
        return None
    if card_str[:-1] not in CARD_NUMBERS or card_str[-1] not in "HDCS":
        return None
    return (CARD_NUMBERS[card_str[:-1]], card_str[-1])

# Check for straight
def is_straight(numbers):
    unique = sorted(set(numbers))
    if len(unique) < 5:
        return False, None
    for i in range(len(unique) - 4):
        if unique[i+4] - unique[i] == 4:
            return True, unique[i+4]
    if set([14, 2, 3, 4, 5]).issubset(set(numbers)):
        return True, 5
    return False, None

# Evaluate poker hand
def evaluate_hand(cards):
    numbers = sorted([n for n, s in cards], reverse=True)
    suits = [s for n, s in cards]
    count_numbers = Counter(numbers)
    is_flush = len(set(suits)) == 1
    is_str, high_straight = is_straight(numbers)

    if is_flush and set(numbers) == set([10, 11, 12, 13, 14]):
        return (9, [])
    if is_flush and is_str:
        return (8, [high_straight])
    for number, count in count_numbers.items():
        if count == 4:
            kicker = max([n for n in numbers if n != number])
            return (7, [number, kicker])
    triples = [n for n, c in count_numbers.items() if c == 3]
    pairs = [n for n, c in count_numbers.items() if c == 2]
    if triples:
        three = max(triples)
        if pairs:
            return (6, [three, max(pairs)])
        if len(triples) > 1:
            return (6, [three, min(triples)])
    if is_flush:
        return (5, numbers)
    if is_str:
        return (4, [high_straight])
    if triples:
        three = max(triples)
        kickers = [n for n in numbers if n != three][:2]
        return (3, [three] + kickers)
    if len(pairs) >= 2:
        top_two = sorted(pairs, reverse=True)[:2]
        kicker = max([n for n in numbers if n not in top_two])
        return (2, top_two + [kicker])
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = [n for n in numbers if n != pair][:3]
        return (1, [pair] + kickers)
    return (0, numbers[:5])

# Comparison logic
def compare_hands(a, b):
    if a[0] != b[0]:
        return a[0] - b[0]
    return (a[1] > b[1]) - (a[1] < b[1])

# ========== Streamlit UI ==========
st.set_page_config(page_title="Poker Evaluator", layout="centered")
st.title("🃏 Poker Hand Evaluator")

if "players" not in st.session_state:
    st.session_state.players = [[]]  # start with 1 player
if "results" not in st.session_state:
    st.session_state.results = [None]

# Button to add a new player
if st.button("➕ Add Player"):
    st.session_state.players.append([])
    st.session_state.results.append(None)

# Input form for each player
for i, _ in enumerate(st.session_state.players):
    st.subheader(f"Player {i+1}")
    cols = st.columns(5)
    hand = []
    for j in range(5):
        card = cols[j].text_input(f"Card {j+1}", key=f"p{i}_c{j}")
        hand.append(card)

    if st.button(f"Check Hand Rank (Player {i+1})"):
        parsed = [parse_card(c) for c in hand]
        if None in parsed:
            st.error(f"Player {i+1}: Invalid card(s) detected.")
        else:
            rank = evaluate_hand(parsed)
            st.session_state.results[i] = rank
            st.success(f"Player {i+1} has a {HAND_RANKS[rank[0]]}")

# Final winner calculation
if st.button("🏆 Find Winner"):
    all_valid = all(r is not None for r in st.session_state.results)
    if not all_valid:
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
