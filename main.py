import re
import requests
from bs4 import BeautifulSoup
from getpass import getpass

def login(sess):
    username = input('Username: ')
    password = getpass()

    sess.get('https://gem.fabtcg.com')
    sess.post(
        url='https://gem.fabtcg.com',
        data={'csrfmiddlewaretoken': sess.cookies.get('csrftoken'), 'username': username, 'password': password},
        headers={'Referer': 'https://gem.fabtcg.com/'})

    return 'sessionid' in sess.cookies.keys()

def calculate_pages(sess):
    # Calculate the number of pages by viewing page 1, and finding the "go to last page" link
    resp = sess.get('https://gem.fabtcg.com/profile/history/?role=player', headers={'Referer': 'https://gem.fabtcg.com/profile/history/'})
    matches = re.findall(r'href=\"\?role=player&amp;page=([0-9]+)\"', resp.text)
    num_pages = 1
    for match in matches:
        page_num = int(match)
        if page_num > num_pages:
            num_pages = page_num
    
    print(f"Number of pages: {num_pages}")
    return num_pages

def parse_page(text):
    soup = BeautifulSoup(text, 'html.parser')

    games = 0
    wins = 0
    byes = 0

    for i, table in enumerate(soup.find_all('table')):
        if 'Record (W-L' not in table.get_text():
            continue # Skip any tables that aren't matchup tables

        for i, row in enumerate(table.find_all('tr')):
            if i == 0:
                continue # Skip the table header

            result = row.find_all('td')[2].string.strip()
            games += 1
            if result == 'Win':
                wins += 1
            elif 'Bye' in result:
                wins += 1
                byes += 1

    return (games, wins, byes)

def calculate_wins(sess, num_pages):
    num_games = 0
    num_wins = 0
    num_byes = 0

    for i in range(1, num_pages+1):
        print(f"Parsing page {i} of results")
        resp = sess.get(f"https://gem.fabtcg.com/profile/history/?role=player&page={i}")

        (games, wins, byes) = parse_page(resp.text)
        num_games += games
        num_wins += wins
        num_byes += byes

    print()
    print(f"Number of games: {num_games}")
    if num_games > 0:
        print(f"Number of wins: {num_wins} ({round(num_wins / num_games * 100)}%)")
        print(f"Number of byes: {num_byes}")
        if num_games > num_byes:
            print(f"Games won: {num_wins - num_byes} ({round((num_wins-num_byes) / (num_games-num_byes) * 100)}%)")

def main():
    with requests.Session() as sess:
        if not login(sess):
            print('Failed to login. Please check your credentials')
            return
        else:
            print('Logged in successfully')

        num_pages = calculate_pages(sess)

        calculate_wins(sess, num_pages)

if __name__ == '__main__':
    main()
