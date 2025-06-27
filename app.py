import streamlit as st  # Import Streamlit library for creating web apps
from collections import Counter  # Import Counter class to count occurrences of items

# -------------------- Step 1: Card Details --------------------
# Dictionary to convert card faces like 'J', 'Q', 'A' to numbers
CARD_NUMBERS = {  # Create dictionary mapping card faces to numeric values
    '2': 2, '3': 3, '4': 4, '5': 5,  # Map number cards to their face values
    '6': 6, '7': 7, '8': 8, '9': 9,  # Continue mapping number cards
    '10': 10, 'J': 11, 'Q': 12,  # Map face cards: Jack=11, Queen=12
    'K': 13, 'A': 14  # Map King=13, Ace=14 (high ace)
}

# Dictionary to map suit letters to visual symbols
SUIT_SYMBOLS = {  # Create dictionary for suit letter to symbol conversion
    'H': '♥',  # Hearts symbol
    'D': '♦',  # Diamonds symbol
    'C': '♣',  # Clubs symbol
    'S': '♠'   # Spades symbol
}

# -------------------- Step 2: Poker Hand Rankings --------------------
# List to assign hand ranking names based on value
HAND_RANKS = [  # List of poker hand rankings from weakest to strongest
    "High Card", "One Pair", "Two Pair", "Three of a Kind",  # Basic hands (ranks 0-3)
    "Straight", "Flush", "Full House", "Four of a Kind",  # Medium hands (ranks 4-7)
    "Straight Flush", "Royal Flush"  # Premium hands (ranks 8-9)
]

# -------------------- Step 3: Convert a card like '10H' into (number, suit) --------------------
def parse_card(card_str):  # Function to convert card string to tuple format
    card_str = card_str.upper().strip()  # Make card string uppercase and remove spaces
    if len(card_str) < 2:  # Check if card string is too short to be valid
        return None  # Return None for invalid input
    number_part = card_str[:-1]  # All characters except last = card number
    suit_part = card_str[-1]     # Last character = suit
    if number_part not in CARD_NUMBERS or suit_part not in "HDCS":  # Validate card number and suit
        return None  # Return None if either part is invalid
    number = CARD_NUMBERS[number_part]  # Convert number string to value (e.g. 'K' to 13)
    return (number, suit_part)  # Return tuple of (numeric_value, suit_letter)

# -------------------- Step 4: Check if numbers form a straight --------------------
def is_straight(numbers):  # Function to check if card numbers form a straight
    unique_numbers = list(set(numbers))  # Remove duplicates
    unique_numbers.sort()                # Sort numbers ascending
    if len(unique_numbers) < 5:  # Need at least 5 unique numbers for a straight
        return False, None  # Return False and None if not enough unique cards

    # Check all windows of size 5
    for i in range(len(unique_numbers) - 4):  # Loop through possible 5-card windows
        first = unique_numbers[i]  # Get first card in current window
        last = unique_numbers[i+4]  # Get last card in current window (5th card)
        if last - first == 4:  # If difference is 4, we have 5 consecutive cards
            return True, last  # Return True and the high card of the straight

    # Handle A, 2, 3, 4, 5 as special case
    if 14 in unique_numbers and all(x in unique_numbers for x in [2, 3, 4, 5]):  # Check for wheel straight (A-2-3-4-5)
        return True, 5  # Return True with 5 as high card for wheel straight

    return False, None  # Return False if no straight found

# -------------------- Step 5: Evaluate Poker Hand --------------------
def evaluate_hand(cards):  # Function to evaluate a 5-card poker hand
    if len(cards) != 5:  # Check if exactly 5 cards provided
        raise ValueError("Hand must contain exactly 5 cards")  # Raise error if not 5 cards
    numbers = [c[0] for c in cards]  # Get numbers like [14, 13, 12, 11, 10]
    suits = [c[1] for c in cards]    # Get suits like ['H', 'H', 'H', 'H', 'H']
    numbers.sort(reverse=True)      # Sort numbers descending for comparison

    count_numbers = Counter(numbers)             # Count how many times each number appears
    all_same_suit = len(set(suits)) == 1         # Check if all suits same => flush
    is_str, high_straight = is_straight(numbers) # Check if it's a straight

    # Check for Royal Flush
    if all_same_suit and set(numbers) == set([10, 11, 12, 13, 14]):  # Check if flush with T-J-Q-K-A
        return (9, [])  # Return rank 9 (Royal Flush) with empty tiebreakers

    # Check for Straight Flush
    if all_same_suit and is_str:  # Check if both flush and straight
        return (8, [high_straight])  # Return rank 8 with high card as tiebreaker

    # Check for Four of a Kind
    for number in count_numbers:  # Loop through each unique card number
        if count_numbers[number] == 4:  # If any number appears 4 times
            kicker = max(n for n in numbers if n != number)  # Find the remaining card (kicker)
            return (7, [number, kicker])  # Return rank 7 with quad value and kicker

    # Check for Full House
    three_of_kind = [n for n in count_numbers if count_numbers[n] == 3]  # Find numbers appearing 3 times
    pairs = [n for n in count_numbers if count_numbers[n] == 2]  # Find numbers appearing 2 times

    if three_of_kind and pairs:  # If we have both three of a kind and a pair
        three = max(three_of_kind)  # Get the highest three of a kind
        return (6, [three, max(pairs)])  # Return rank 6 (Full House) with trips and pair

    # Check for Flush
    if all_same_suit:  # If all cards are same suit but not straight
        return (5, numbers)  # Return rank 5 with all card values as tiebreakers

    # Check for Straight
    if is_str:  # If cards form straight but not same suit
        return (4, [high_straight])  # Return rank 4 with high card of straight

    # Check for Three of a Kind
    if three_of_kind:  # If we have three of a kind but no pair
        three = max(three_of_kind)  # Get the three of a kind value
        kickers = [n for n in numbers if n != three][:2]  # Get top 2 remaining cards as kickers
        return (3, [three] + kickers)  # Return rank 3 with trips value and kickers

    # Check for Two Pair
    if len(pairs) >= 2:  # If we have at least 2 pairs
        sorted_pairs = sorted(pairs, reverse=True)[:2]  # Get top 2 pairs in descending order
        kicker = max(n for n in numbers if n not in sorted_pairs)  # Find remaining card as kicker
        return (2, sorted_pairs + [kicker])  # Return rank 2 with both pairs and kicker

    # Check for One Pair
    if len(pairs) == 1:  # If we have exactly one pair
        pair = pairs[0]  # Get the pair value
        kickers = [n for n in numbers if n != pair][:3]  # Get top 3 remaining cards as kickers
        return (1, [pair] + kickers)  # Return rank 1 with pair value and kickers

    # High Card
    return (0, numbers[:5])  # Return rank 0 with top 5 cards as tiebreakers

# -------------------- Step 6: Compare Two Hands --------------------
def compare_hands(a, b):  # Function to compare two evaluated hands
    if a[0] != b[0]:  # If hand ranks are different
        return a[0] - b[0]  # Compare rank
    # Compare tiebreaker arrays element by element
    for i in range(min(len(a[1]), len(b[1]))):  # Loop through tiebreaker values
        if a[1][i] != b[1][i]:  # If tiebreaker values are different
            return a[1][i] - b[1][i]  # Return difference of tiebreaker values
    return 0  # Return 0 if hands are exactly equal

# -------------------- Streamlit UI Setup --------------------
st.set_page_config(page_title="Poker Evaluator", layout="centered")  # Configure Streamlit page settings
st.title("🃏 Poker Hand Evaluator")  # Display main title with card emoji
st.text("Write in the format card_number+card_suite, so for eg. Ace of Spades and 9 of Clubs are AS or as and 9c or 9C respectively") 

# Initialize state variables
if "players" not in st.session_state:  # Check if players list exists in session state
    st.session_state.players = [[]]  # Initialize with one empty player
if "results" not in st.session_state:  # Check if results list exists in session state
    st.session_state.results = [None]  # Initialize with one None result
if "disable_check" not in st.session_state:  # Check if disable_check list exists in session state
    st.session_state.disable_check = [False]  # Initialize with one False value

# Add new player button
if st.button("➕ Add Player"):  # Create button to add new player
    st.session_state.players.append([])  # Add empty list for new player's cards
    st.session_state.results.append(None)  # Add None result for new player
    st.session_state.disable_check.append(False)  # Add False disable state for new player

# -------------------- Used Card Validation Setup --------------------
used_set = set()     # Tracks all unique cards already used
card_dict = {}       # Maps each card to which player index it belongs to

# Rebuild card_dict fresh each time to track all cards
for i in range(len(st.session_state.players)):  # Loop through each player
    for j in range(5):  # Loop through each of 5 card positions
        card = st.session_state.get(f"p{i}_c{j}", "").strip().upper()  # Get card input, clean it
        if card:  # If card input is not empty
            if card in used_set:  # If card is already used by another player
                card_dict[card].append(i)  # Add current player to list of users of this card
            else:  # If card is new
                card_dict[card] = [i]  # Create new entry with current player
                used_set.add(card)  # Add card to used set

# -------------------- Input Cards For Each Player --------------------
for i in range(len(st.session_state.players)):  # Loop through each player
    st.subheader(f"Player {i+1}")  # Display player number as subheader
    cols = st.columns(5)  # Layout for 5 cards
    current_hand = []  # Initialize list to store current player's hand

    for j in range(5):  # Loop through 5 card input positions
        key = f"p{i}_c{j}"  # Create unique key for this card input
        card_input = cols[j].text_input(f"Card {j+1}", key=key)  # Create text input in column j
        card = card_input.strip().upper()  # Clean and uppercase the input
        current_hand.append(card)  # Add card to current hand list

        if parse_card(card):  # If valid card, show preview with symbol
            card_number, suit = parse_card(card)  # Parse card into number and suit
            cols[j].markdown(f"### {card[:-1]} {SUIT_SYMBOLS.get(suit, '?')}")  # Display card with symbol

    parsed = [parse_card(c) for c in current_hand]  # Convert card strings to tuples
    card_ids = [c for c in current_hand]             # Store raw input strings

    stored_hand_key = f"stored_hand_{i}"  # Create key for storing previous hand state
    prev_hand = st.session_state.get(stored_hand_key, ["" for _ in range(5)])  # Get previous hand or default empty

    # If player changed any card, re-enable button
    if card_ids != prev_hand:  # Compare current hand to previous hand
        st.session_state.results[i] = None  # Reset result for this player
        st.session_state.disable_check[i] = False  # Re-enable check button

    # -------------------- Check Hand Rank Button --------------------
    if st.button(f"Check Hand Rank (Player {i+1})", disabled=st.session_state.disable_check[i]):  # Create check button
        if None in parsed:  # If any card failed to parse
            st.error(f"Player {i+1}: Invalid card(s).")  # Show error for invalid cards
        elif len(set(card_ids)) < 5:  # If there are duplicate cards in hand
            st.error(f"Player {i+1}: Duplicate cards in hand.")  # Show error for duplicates
        elif any(len(card_dict[c]) > 1 for c in card_ids):  # If any card is used by multiple players
            st.error(f"Player {i+1}: Card already used by another player.")  # Show error for shared cards
        else:  # If all validations pass
            result = evaluate_hand(parsed)  # Evaluate the poker hand
            st.session_state.results[i] = result  # Store result in session state
            st.session_state.disable_check[i] = True  # Disable button after checking
            st.session_state[stored_hand_key] = card_ids.copy()  # Store current hand for comparison
            st.success(f"Player {i+1} has a {HAND_RANKS[result[0]]}")  # Show success message with hand rank

# -------------------- Find Winner Button --------------------
if st.button("🏆 Find Winner"):  # Create button to determine winner
    if any(r is None for r in st.session_state.results):  # If any player hasn't been evaluated
        st.warning("Please check all players' hands first.")  # Show warning message
    else:  # If all players have been evaluated
        best = max(st.session_state.results)  # Find the best hand result
        winners = [i+1 for i, r in enumerate(st.session_state.results) if r == best]  # Find all players with best hand

        for i, r in enumerate(st.session_state.results):  # Loop through all results
            st.write(f"Player {i+1}: {HAND_RANKS[r[0]]}")  # Display each player's hand rank

        if len(winners) == 1:  # If there's only one winner
            st.success(f"🏆 Player {winners[0]} wins with a {HAND_RANKS[best[0]]}!")  # Show winner message
        else:  # If there's a tie
            st.info(f"🤝 It's a tie between players: {', '.join(str(w) for w in winners)}")  # Show tie message

# -------------------- Reset Button --------------------
if st.button("🔄 Reset All"):  # Create reset button
    st.session_state.clear()  # Clear all session state variables
    st.rerun()  # Rerun the app to refresh the interface

# You can comment out the single-deck restriction by removing the used_set/card_dict logic if needed.
