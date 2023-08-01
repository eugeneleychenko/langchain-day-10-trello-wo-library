import streamlit as st
import requests
from dotenv import load_dotenv
import os
from fuzzywuzzy import fuzz
import json

load_dotenv()
API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TOKEN")
BASE_URL = 'https://api.trello.com/1/'

def get_all_boards():
    try:
        url = f'{BASE_URL}members/me/boards'
        query = {
            'key': API_KEY,
            'token': TOKEN
        }
        response = requests.get(url, params=query)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except ValueError as e:
        st.error(f"Error parsing response as JSON: {e}")
    return []

def get_all_lists_on_board(board_id):
    try:
        url = f'{BASE_URL}boards/{board_id}/lists'
        query = {
            'key': API_KEY,
            'token': TOKEN
        }
        response = requests.get(url, params=query)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except json.JSONDecodeError as e:
        st.error(f"Error decoding response as JSON: {e}")
    return []

def get_all_cards_on_board(board_id):
    try:
        url = f'{BASE_URL}boards/{board_id}/cards'
        query = {
            'key': API_KEY,
            'token': TOKEN
        }
        response = requests.get(url, params=query)
        response.raise_for_status()
        
        # Check if the server returned a response
        if response.status_code != 200:
            st.error(f"Error: Received status code {response.status_code}")
            return None

        # Check if the response is not empty
        if not response.text:
            st.error("Error: Received empty response")
            return None

        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except json.JSONDecodeError as e:
        st.error(f"Error decoding response as JSON: {e}")
    return None

    # Try to parse the response as JSON
    try:
        cards = response.json()
    except json.JSONDecodeError:
        st.error("Error: Response is not valid JSON")
        return None

    return cards

def make_comment_on_card(card_id, comment):
    try:
        url = f'{BASE_URL}cards/{card_id}/actions/comments'
        query = {
            'key': API_KEY,
            'token': TOKEN,
            'text': comment
        }
        response = requests.post(url, params=query)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except ValueError as e:
        st.error(f"Error parsing response as JSON: {e}")
    return []

def move_card_to_list(card_id, list_id):
    try:
        url = f'{BASE_URL}cards/{card_id}'
        query = {
            'key': API_KEY,
            'token': TOKEN,
            'idList': list_id
        }
        response = requests.put(url, params=query)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except ValueError as e:
        st.error(f"Error parsing response as JSON: {e}")
    return []

def fuzzy_search_board(board_name):
    boards = get_all_boards()
    matches = [(board, fuzz.ratio(board_name, board['name'])) for board in boards]
    best_match = max(matches, key=lambda match: match[1])
    return best_match[0] if best_match[1] > 60 else None

def fuzzy_search_card(board_id, card_name):
    cards = get_all_cards_on_board(board_id)
    if cards is None:
        st.error(f"Could not fetch cards for board ID {board_id}")
        return None
    matches = [(card, fuzz.ratio(card_name, card['name'])) for card in cards]
    best_match = max(matches, key=lambda match: match[1])
    return best_match[0] if best_match[1] > 60 else None

def fuzzy_search_list(board_id, list_name):
    lists = get_all_lists_on_board(board_id)
    matches = [(lst, fuzz.ratio(list_name, lst['name'])) for lst in lists]
    best_match = max(matches, key=lambda match: match[1])
    return best_match[0] if best_match[1] > 60 else None

def move_card_to_list_fuzzy(board_name, card_name, list_name):
    board = fuzzy_search_board(board_name)
    if not board:
        st.warning(f"No board found with name {board_name}")
        return
    card = fuzzy_search_card(board['id'], card_name)
    if not card:
        st.warning(f"No card found with name {card_name}")
        return
    lst = fuzzy_search_list(board['id'], list_name)
    if not lst:
        st.warning(f"No list found with name {list_name}")
        return
    move_card_to_list(card['id'], lst['id'])

def comment_on_card_fuzzy(board_name, card_name, comment):
    board = fuzzy_search_board(board_name)
    if not board:
        st.warning(f"No board found with name {board_name}")
        return
    card = fuzzy_search_card(board['id'], card_name)
    if not card:
        st.warning(f"No card found with name {card_name}")
        return
    make_comment_on_card(card['id'], comment)

# Streamlit app
st.title("Trello API Integration")

# Get all boards
st.header("Get All Boards")
if st.button("Fetch Boards"):
    boards = get_all_boards()
    st.write(boards)

# Get all lists on a board
st.header("Get All Lists on Board")
board_id = st.text_input("Enter board ID:", key="list_board_id")
if st.button("Fetch Lists"):
    lists = get_all_lists_on_board(board_id)
    st.write(lists)

# Get all cards on a board
st.header("Get All Cards on Board")
board_id = st.text_input("Enter board ID:", key="cards_board_id")
if st.button("Fetch Cards"):
    cards = get_all_cards_on_board(board_id)
    st.write(cards)

# Make a comment on a card
st.header("Make Comment on Card")
card_id = st.text_input("Enter card ID:", key="comment_card_id")
comment = st.text_input("Enter comment:", key="comment_text")
if st.button("Make Comment"):
    make_comment_on_card(card_id, comment)

# Move a card to a list
st.header("Move Card to List")
card_id = st.text_input("Enter card ID:", key="move_card_id")
list_id = st.text_input("Enter list ID:", key="move_list_id")
if st.button("Move Card"):
    move_card_to_list(card_id, list_id)

# Fuzzy search and move card to list
st.header("Fuzzy Search and Move Card to List")
board_name = st.text_input("Enter board name:", key="fuzzy_board_name")
card_name = st.text_input("Enter card name:", key="fuzzy_card_name")
list_name = st.text_input("Enter list name:", key="fuzzy_list_name")
if st.button("Fuzzy Search and Move"):
    move_card_to_list_fuzzy(board_name, card_name, list_name)

# Fuzzy search and make comment on card
st.header("Fuzzy Search and Make Comment on Card")
board_name = st.text_input("Enter board name:", key="fuzzy_comment_board_name")
card_name = st.text_input("Enter card name:", key="fuzzy_comment_card_name")
comment = st.text_input("Enter comment:", key="fuzzy_comment_text")
if st.button("Fuzzy Search and Comment"):
    comment_on_card_fuzzy(board_name, card_name, comment)