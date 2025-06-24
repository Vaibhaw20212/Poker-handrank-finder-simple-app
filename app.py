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
    card_str = card_str.upper().strip()  # Make it uppercase and remove spaces

    # A card must be at least 2 characters, like '2H'
    if len(card_str) < 2:
        return None

    # The card number should be valid and suit should be H, D, C, or S
    number_part = card_str[:-1]  # everything except last character
    suit_part = card_str[-1]     # last character is suit

    if number_part not in CARD_NUMBERS:
        return None
    if suit_part not in "HDCS":
        return None

    number = CARD_NUMBERS[number_part]  # convert to number
    return (number, suit_part)  # return as a pair (number, suit)

# Step 4: Check if a list of card numbers is a straight
# (i.e., five cards in a row like 5-6-7-8-9)
def is_straight(numbers):
    unique_numbers = list(set(numbers))  # remove duplicates
    unique_numbers.sort()  # sort the list in increasing order

    if len(unique_numbers) < 5:
        return False, None  # not enough unique cards for a straight

    # Try all possible 5-length sequences
    for i in range(len(unique_numbers) - 4):
        first = unique_numbers[i]
        last = unique_numbers[i + 4]
        if last - first == 4:
            return True, last  # found a straight ending at this card number

    # Check special case for A-2-3-4-5
    if 14 in unique_numbers and all(x in unique_numbers for x in [2, 3, 4, 5]):
        return True, 5

    return False, None  # not a straight

# Step 5: Evaluate a player's hand and decide its type and strength
# Input is a list of 5 (number, suit) pairs
def evaluate_hand(cards):
    numbers = []
    suits = []

    for card in cards:
        number, suit = card
        numbers.append(number)
        suits.append(suit)

    numbers.sort(reverse=True)  # sort numbers from high to low

    # Count how many times each number appears
    count_numbers = Counter(numbers)

    # Check if all cards are the same suit
    all_same_suit = len(set(suits)) == 1

    # Check if it's a straight
    is_str, high_straight = is_straight(numbers)

    # Check for Royal Flush (10 to Ace, all same suit)
    if all_same_suit and set(numbers) == set([10, 11, 12, 13, 14]):
        return (9, [])

    # Check for Straight Flush
    if all_same_suit and is_str:
        return (8, [high_straight])

    # Check for Four of a Kind
    for number in count_numbers:
        if count_numbers[number] == 4:
            kicker = max(n for n in numbers if n != number)
            return (7, [number, kicker])

    # Check for Full House (3 of one kind and 2 of another)
    three_of_kind = [n for n in count_numbers if count_numbers[n] == 3]
    pairs = [n for n in count_numbers if count_numbers[n] == 2]

    if three_of_kind:
        three = max(three_of_kind)
        if pairs:
            return (6, [three, max(pairs)])
        if len(three_of_kind) > 1:
            return (6, [three, min(three_of_kind)])

    # Check for Flush
    if all_same_suit:
        return (5, numbers)

    # Check for Straight
    if is_str:
        return (4, [high_straight])

    # Check for Three of a Kind
    if three_of_kind:
        three = max(three_of_kind)
        kickers = [n for n in numbers if n != three][:2]
        return (3, [three] + kickers)

    # Check for Two Pair
    if len(pairs) >= 2:
        sorted_pairs = sorted(pairs, reverse=True)[:2]
        kicker = max(n for n in numbers if n not in sorted_pairs)
        return (2, sorted_pairs + [kicker])

    # Check for One Pair
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = [n for n in numbers if n != pair][:3]
        return (1, [pair] + kickers)

    # If none of the above, return High Card
    return (0, numbers[:5])

# Step 6: Compare two hands and return winner
# Return positive if a > b, negative if b > a, 0 if equal
def compare_hands(a, b):
    if a[0] != b[0]:
        return a[0] - b[0]  # higher rank wins
    return (a[1] > b[1]) - (a[1] < b[1])  # if rank same, use tiebreaker values

# Step 7: Streamlit app starts here

# Set up the web page layout
st.set_page_config(page_title="Poker Evaluator", layout="centered")
st.title("🃏 Poker Hand Evaluator")

# Setup memory for players and results
if "players" not in st.session_state:
    st.session_state.players = [[]]  # player hands
if "results" not in st.session_state:
    st.session_state.results = [None]  # evaluation results
if "used_cards" not in st.session_state:
    st.session_state.used_cards = set()  # to track duplicate cards across players

# Button to add another player
if st.button("➕ Add Player"):
    st.session_state.players.append([])
    st.session_state.results.append(None)

# Section for each player's input
for i, _ in enumerate(st.session_state.players):
    st.subheader(f"Player {i+1}")
    cols = st.columns(5)
    hand = []
    for j in range(5):
        card = cols[j].text_input(f"Card {j+1}", key=f"p{i}_c{j}")
        hand.append(card)

    # Button to check hand rank
    if st.button(f"Check Hand Rank (Player {i+1})"):
        parsed = [parse_card(c) for c in hand]
        card_ids = [c.upper().strip() for c in hand]  # original format for tracking

        # Check for invalid or repeated cards
        if None in parsed:
            st.error(f"Player {i+1}: Invalid card(s).")
        elif len(set(card_ids)) < 5:
            st.error(f"Player {i+1}: Duplicate cards in hand.")
        elif any(c in st.session_state.used_cards for c in card_ids):
            st.error(f"Player {i+1}: Card already used by another player.")
        else:
            for c in card_ids:
                st.session_state.used_cards.add(c)  # remember used cards
            result = evaluate_hand(parsed)  # calculate hand type
            st.session_state.results[i] = result  # store result
            hand_type_index = result[0]
            hand_type_name = HAND_RANKS[hand_type_index]
            st.success(f"Player {i+1} has a {hand_type_name}")

# Button to decide the final winner
if st.button("🏆 Find Winner"):
    # Check that all players have valid results
    all_valid = all(r is not None for r in st.session_state.results)
    if not all_valid:
        st.warning("Please check all players' hands first.")
    else:
        # Find the best hand
        best = max(st.session_state.results)
        winners = []

        for index, result in enumerate(st.session_state.results):
            hand_name = HAND_RANKS[result[0]]
            st.write(f"Player {index+1}: {hand_name}")
            if result == best:
                winners.append(index + 1)

        # Announce winner(s)
        if len(winners) == 1:
            st.success(f"🏆 Player {winners[0]} wins with a {HAND_RANKS[best[0]]}!")
        else:
            winner_names = ", ".join(str(w) for w in winners)
            st.info(f"🤝 It's a tie between players: {winner_names}")

# Note: You can comment out the used_cards checks if you want to test with duplicate cards.
