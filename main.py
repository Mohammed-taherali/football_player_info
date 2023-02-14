# Imports
from bs4 import BeautifulSoup
import requests
import re

# Main website
website = r'https://fbref.com/en/'

def get_player_link():
    # Get the name of the player
    two_letters = input("Enter first two letters of player name: ")
    player_name = input("Enter name of player: ")
    player_name = player_name.title().replace(' ', '-')

    # Get the HTML content of the website
    source = requests.get(f'{website}players/{two_letters}/').text
    soup = BeautifulSoup(source, 'lxml')

    # Get the 'div' containing the names and 
    # info of all player whose names are starting with the given two letters
    article = soup.find('div', class_="section_content")
    results = article.find_all('p')

    # Find the link to the player's page.
    info_link = None
    player_id = None 
    for info in results:
        name = info.a.get("href").split('/')[-1]
        if player_name.lower() == name.lower():
            # print("found")
            player_id = info.a.get("href").split('/')[-2]
            info_link = f'{website}players/{player_id}/scout/365_m1/{player_name}-Scouting-Report'
            break

    return (info_link, player_name, player_id)

def player_stats():
    
    info_link, player_name, player_id = get_player_link()

    if not info_link:
        print("Please check the spelling of the player. \nThe first two initials must be of the main name of the player")
        print("For eg: For ronaldo: ro \nFor messi: me \nFor neymar: ne")
        exit()

    # Get text of the player info page
    src = requests.get(info_link).text
    soup = BeautifulSoup(src, 'lxml')
    
    # Get all information articles.
    gen_info_art = soup.find("div", attrs={"id":"meta"}).find_all('div')[-1].find_all('p')
    try:
        awards_art = soup.find('ul', attrs={"id": "bling"}).find_all('a')
    except:
        awards_art = None
    try:
        stats_art = soup.find('table', attrs={"id": re.compile('^scout_full_')}).find('tbody')
        for tr in stats_art.find_all('tr', class_=["spacer", "partial_table"]):
            tr.extract()
        stats_art = stats_art.find_all('tr')
    except:
        stats_art = None

    # Create a file to write.
    with open(f"{player_name}-info.txt", "w", encoding="utf-8") as f:
        f.write(f"\t\t\t{player_name.replace('-', ' ').upper()}\n\n")
        
        # General information about player.
        f.write("\t\t\tGeneral information\n\n")
        for stat in gen_info_art:
            res = " ".join(line.strip() for line in stat.text.strip().split("\n"))
            f.write(res + '\n')

        # Achievements and awards.
        if awards_art:
            f.write("\n\n\t\t\tAwards\n")
            for award in awards_art:
                f.write(award.text + '\n')

        if stats_art:
            col1_width = 35
            col2_width = 11
            col3_width = 11
            # All statistics
            f.write("\n\n\t\t\tStandard Stats\n")
            f.write("STATISTIC" + " " * (col1_width - len("STATISTIC")) + "|")
            f.write("Per 90" + " " * (col2_width - len("Per 90")) + "|")
            f.write("Percentile" + " " * (col3_width - len("Percentile")) + "|\n")
            for row in stats_art:
                if row.get("class") == ["thead", "over_header", "thead"]:
                    f.write(f"\n\n\t\t\t{row.th.text}\n")
                elif row.get("class") == ["thead", "thead"]:
                    f.write("STATISTIC" + " " * (col1_width - len("STATISTIC")) + "|")
                    f.write("Per 90" + " " * (col2_width - len("Per 90")) + "|")
                    f.write("Percentile" + " " * (col3_width - len("Percentile")) + "|\n")
                else:
                    f.write(row.th.text + " " * (col1_width - len(row.th.text)) + "|")
                    for td in row.find_all("td"):
                        f.write(td.text + " " * (col2_width - len(td.text)) + "|")
                    f.write("\n")


if __name__ == "__main__":
    player_stats()