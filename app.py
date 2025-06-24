import streamlit as st
from collections import Counter

# ===============================
# Step 1: Define card values and ranking names
# ===============================

# This dictionary maps card symbols (like 'J') to numbers
CARD_NUMBERS = {
    '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12,
    'K': 13, 'A': 14
}

# Human-readable version (not used, just for display if needed)
REVERSE_NUMBERS = {v: k for k, v in CARD_NUMBERS.items()}

# Poker hand types ranked from weakest to strongest
HAND_RANKS = [
    "High Card",
    "One Pair",
    "Two Pair",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush",
    "Royal Flush"
]

# ===============================
# Step 2: Helper Functions
# ===============================

# Convert a card string like '10H' or 'AS' into (card_number, suit)
def parse_card(card_str):
    card_str = card_str.upper().strip()
    if len(card_str) < 2:
        return None
    if card_str[:-1] not in CARD_NUMBERS or card_str[-1] not in "HDCS":
        return None
    return (CARD_NUMBERS[card_str[:-1]], card_str[-1])  # (number, suit)

# Check if a list of card numbers forms a straight (5 in a row)
def is_straight(numbers):
    unique = sorted(set(numbers))  # Remove duplicates
    if len(unique) < 5:
        return False, None
    for i in range(len(unique) - 4):  # i runs through the index of card numbers
        if unique[i+4] - unique[i] == 4:
            return True, unique[i+4]
    # Special case: A-2-3-4-5
    if set([14, 2, 3, 4, 5]).issubset(set(numbers)):
        return True, 5
    return False, None

# Evaluate a player's hand of 5 cards
def evaluate_hand(cards):
    numbers = sorted([n for n, s in cards], reverse=True)  # n = card number
    suits = [s for n, s in cards]
    count_numbers = Counter(numbers)
    is_flush = len(set(suits)) == 1
    is_str, high_straight = is_straight(numbers)

    # Royal Flush
    if is_flush and set(numbers) == set([10, 11, 12, 13, 14]):
        return (9, [])

    # Straight Flush
    if is_flush and is_str:
        return (8, [high_straight])

    # Four of a Kind
    for number, count in count_numbers.items():  # number = card value, count = how many times it appears
        if count == 4:
            kicker = max([n for n in numbers if n != number])
            return (7, [number, kicker])

    # Full House
    triples = [n for n, c in count_numbers.items() if c == 3]
    pairs = [n for n, c in count_numbers.items() if c == 2]
    if triples:
        three = max(triples)
        if pairs:
            return (6, [three, max(pairs)])
        if len(triples) > 1:
            return (6, [three, min(triples)])

    # Flush
    if is_flush:
        return (5, numbers)

    # Straight
    if is_str:
        return (4, [high_straight])

    # Three of a Kind
    if triples:
        three = max(triples)
        kickers = [n for n in numbers if n != three][:2]
        return (3, [three] + kickers)

    # Two Pair
    if len(pairs) >= 2:
        top_two = sorted(pairs, reverse=True)[:2]
        kicker = max([n for n in numbers if n not in top_two])
        return (2, top_two + [kicker])

    # One Pair
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = [n for n in numbers if n != pair][:3]
        return (1, [pair] + kickers)

    # High Card
    return (0, numbers[:5])

# Compare two hands by rank and tie-breaker values
def compare_hands(a, b):
    if a[0] != b[0]:
        return a[0] - b[0]
    return (a[1] > b[1]) - (a[1] < b[1])

# ===============================
# Step 3: Streamlit Interface
# ===============================

st.title("🃏 Poker Hand Evaluator for 6 Players")
st.write("Enter 5 cards for each player using format like `AH`, `10S`, `2D`, etc.")

players = []

# Loop through 6 players to get 5 cards each
for i in range(6):  # i goes from 0 to 5 → Player 1 to Player 6
    with st.expander(f"Player {i+1} Cards"):
        inputs = []
        cols = st.columns(5)
        for j in range(5):  # j goes from 0 to 4 → Card 1 to Card 5
            card = cols[j].text_input(f"Card {j+1}", key=f"p{i}_c{j}")
            inputs.append(card)
        players.append(inputs)

# Button to evaluate
if st.button("Evaluate Hands"):
    valid = True
    parsed_players = []

    # Convert text cards to structured form: (number, suit)
        used_cards = set()  # To track already-entered cards (for duplicate check)

    for idx, hand in enumerate(players):  # idx = player index
        parsed = []
        for c in hand:  # c = card string like 'AS'
            card = parse_card(c)
            if not card:
                st.error(f"Invalid card '{c}' for Player {idx+1}. Use format like '10S', 'AH', etc.")
                valid = False
                break

            card_str = c.upper().strip()

            # === Uncomment the block below to enforce one-deck rule (no duplicate cards) ===
            # if card_str in used_cards:
            #     st.error(f"Card '{card_str}' has already been used. Only one standard deck is allowed.")
            #     valid = False
            #     break
            # used_cards.add(card_str)
            # ===========================================================================

            parsed.append(card)

        if not valid:
            break
        parsed_players.append(parsed)


    if valid:
        results = []
        for p in parsed_players:  # p is a player's hand of 5 (number, suit) cards
            rank = evaluate_hand(p)
            results.append(rank)

        # Find best hand (highest ranking number)
        best_rank = max(results)
        winners = [i+1 for i, r in enumerate(results) if r == best_rank]

        st.subheader("Results")
        for i, rank in enumerate(results):  # i = player index, rank = (hand type index, tiebreakers)
            name = HAND_RANKS[rank[0]]
            st.write(f"Player {i+1}: **{name}**")

        if len(winners) == 1:
            st.success(f"Player {winners[0]} wins with a {HAND_RANKS[best_rank[0]]}!")
        else:
            st.warning(f"It's a tie between players: {', '.join(str(w) for w in winners)} (all have {HAND_RANKS[best_rank[0]]})")
