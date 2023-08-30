from termcolor import colored

def show_start_menu():
    print(colored("Создатель - QIYANA", "green"))
    print(colored("LOLZ - " + colored("https://zelenka.guru/sataraitsme/", "blue"), "yellow"))
    print(colored("TG - " + colored("t.me/sataraitsme", "magenta"), "cyan"))
    print()

show_start_menu()

summoner_name = input("Введите ник для анализа: ")
summoner_url = f"https://ru.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
champion_ids_file = "champion_ids.txt"

import requests
from tabulate import tabulate

headers = {
    "X-Riot-Token": "здесь укажи свой рито апи"
}

champion_ids = {}
with open(champion_ids_file, "r") as f:
    for line in f:
        parts = line.strip().split("\t")
        champion_id = int(parts[0])
        champion_name = parts[1]
        champion_ids[champion_id] = champion_name

summoner_response = requests.get(summoner_url, headers=headers)
if summoner_response.status_code == 200:
    summoner_data = summoner_response.json()
    summoner_name = summoner_data["name"]
    summoner_level = summoner_data["summonerLevel"]
    
    account_url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{summoner_data['puuid']}"
    rank_url = f"https://ru.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_data['id']}"
    mastery_url = f"https://ru.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_data['id']}"
    
    rank_response = requests.get(rank_url, headers=headers)
    
    mastery_response = requests.get(mastery_url, headers=headers)
    
    if (
        rank_response.status_code == 200
        and mastery_response.status_code == 200
    ):
        print(f"Ник: {summoner_name}")
        print(f"Уровень: {summoner_level}")
        
        rank_data = rank_response.json()
        if len(rank_data) > 0:
            rank_tables = []
            for rank_entry in rank_data:
                queue_type = rank_entry["queueType"]
                if queue_type != "RANKED_TFT":
                    tier = rank_entry.get("tier", "Неизвестно")
                    rank = rank_entry.get("rank", "Неизвестно")
                    wins = rank_entry.get("wins", "Неизвестно")
                    losses = rank_entry.get("losses", "Неизвестно")
                    
                    rank_info = [
                        ["Тип очереди", queue_type],
                        ["Тир", tier],
                        ["Ранг", rank],
                        ["Победы", wins],
                        ["Поражения", losses]
                    ]
                    
                    rank_tables.append((f"Ранг для {queue_type}", tabulate(rank_info, tablefmt="grid")))
            
            for rank_table in rank_tables:
                print(rank_table[0])
                print(rank_table[1])
        else:
            print("Призыватель не имеет ранговой информации.")
        
        mastery_data = mastery_response.json()
        if len(mastery_data) > 0:
            mastery_table = []
            for mastery in mastery_data:
                champion_id = mastery["championId"]
                champion_level = mastery["championLevel"]
                champion_points = mastery["championPoints"]
                
                champion_name = champion_ids.get(champion_id, f"Чемпион {champion_id}")
                
                mastery_table.append([f"{champion_name}", champion_id, champion_level, champion_points])
            
            print(tabulate(mastery_table, headers=["Ник Чемпиона", "ID", "Уровень мастерства", "Очки мастерства"], tablefmt="grid"))
        else:
            print("Призыватель не имеет информации о мастерстве.")
    else:
        print(f"Произошла ошибка при запросе. Код ошибки: {rank_response.status_code}")
else:
    print(f"Произошла ошибка при запросе. Код ошибки: {summoner_response.status_code}")
