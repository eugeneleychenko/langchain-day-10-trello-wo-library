import streamlit as st
import requests
from dotenv import load_dotenv
import os
from fuzzywuzzy import fuzz

load_dotenv()
API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TOKEN")
BASE_URL = 'https://api.trello.com/1/'

def get_all_boards():
    url = f'{BASE_URL}members/me/boards'
    query = {
        'key': API_KEY,
        'token': TOKEN
    }
    response = requests.get(url, params=query)
    return response.json()

def get_all_lists_on_board(board_id):
    url = f'{BASE_URL}boards/{board_id}/lists'
    query = {
        'key': API_KEY,
        'token': TOKEN
    }
    response = requests.get(url, params=query)
    return response.json()

def make_comment_on_card(card_id, comment):
    url = f'{BASE_URL}cards/{card_id}/actions/comments'
    query = {
        'key': API_KEY,
        'token': TOKEN,
        'text': comment
    }
    response = requests.post(url, params=query)
    return response.json()

def move_card_to_list(card_id, list_id):
    url = f'{BASE_URL}cards/{card_id}'
    query = {
        'key': API_KEY,
        'token': TOKEN,
        'idList': list_id
    }
    response = requests.put(url, params=query)
    return response.json()

def fuzzy_search_board(board_name):
    boards = get_all_boards()
    matches = [(board, fuzz.ratio(board_name, board['name'])) for board in boards]
    best_match = max(matches, key=lambda match: match[1])
    return best_match[0] if best_match[1] > 50 else None

def fuzzy_search_card(board_id, card_name):
    lists = get_all_lists_on_board(board_id)
    cards = []
    for lst in lists:
        url = f'{BASE_URL}lists/{lst["id"]}/cards'
        query = {
            'key': API_KEY,
            'token': TOKEN
        }
        response = requests.get(url, params=query)
        cards.extend(response.json())
    matches = [(card, fuzz.ratio(card_name, card['name'])) for card in cards]
    best_match = max(matches, key=lambda match: match[1])
    return best_match[0] if best_match[1] > 30 else None

st.title('Trello Manager')

if st.button('Get All Boards'):
    boards = get_all_boards()
    st.write(boards)

board_name = st.text_input('Enter Board Name to Search')
if board_name and st.button('Fuzzy Search Board'):
    board = fuzzy_search_board(board_name)
    if board:
        st.write(f'Board found: {board["name"]}')
    else:
        st.write('No matching board found.')

board_id = st.text_input('Enter Board ID to Get All Lists')
if board_id and st.button('Get All Lists'):
    lists = get_all_lists_on_board(board_id)
    st.write(lists)

card_name = st.text_input('Enter Card Name to Search')
if board_id and card_name and st.button('Fuzzy Search Card'):
    card = fuzzy_search_card(board_id, card_name)
    if card:
        st.write(f'Card found: {card["name"]}')
    else:
        st.write('No matching card found.')

card_id = st.text_input('Enter Card ID to Comment')
comment = st.text_input('Enter Comment')
if card_id and comment and st.button('Make Comment'):
    comment_response = make_comment_on_card(card_id, comment)
    st.write(comment_response)

card_id_to_move = st.text_input('Enter Card ID to Move')
list_id_to_move = st.text_input('Enter List ID to Move Card To')
if card_id_to_move and list_id_to_move and st.button('Move Card'):
    move_response = move_card_to_list(card_id_to_move, list_id_to_move)
    st.write(move_response)