api_key = "RGAPI-e9d09244-80d6-4261-9a6a-cfd44c827fee"
summoner_name = input("Введите ник для анализа: ")
summoner_url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
champion_ids_file = "champion_ids.txt"

import requests
from tabulate import tabulate

headers = {
    "X-Riot-Token": "RGAPI-fec0536a-5c54-40d6-8e6e-795509a90a47"
}

# Загружаем файл с соответствиями ID чемпионов и их ников
champion_ids = {}
with open(champion_ids_file, "r") as f:
    for line in f:
        parts = line.strip().split("\t")
        champion_id = int(parts[0])
        champion_name = parts[1]
        champion_ids[champion_id] = champion_name

# Получаем информацию о призывателе
summoner_response = requests.get(summoner_url, headers=headers)
if summoner_response.status_code == 200:
    summoner_data = summoner_response.json()
    summoner_name = summoner_data["name"]
    summoner_level = summoner_data["summonerLevel"]
    
    account_url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{summoner_data['puuid']}"
    rank_url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_data['id']}"
    mastery_url = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_data['id']}"
    
    # Получаем информацию о ранге призывателя
    rank_response = requests.get(rank_url, headers=headers)
    
    # Получаем информацию о мастерстве по чемпионам
    mastery_response = requests.get(mastery_url, headers=headers)
    
    if (
        rank_response.status_code == 200
        and mastery_response.status_code == 200
    ):
        # Создаем строку для сохранения в файл
        stat_text = f"Ник: {summoner_name}\nУровень: {summoner_level}\n"
        
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
                stat_text += f"{rank_table[0]}\n{rank_table[1]}\n"
        else:
            stat_text += "Призыватель не имеет ранговой информации.\n"
        
        mastery_data = mastery_response.json()
        if len(mastery_data) > 0:
            mastery_table = []
            for mastery in mastery_data:
                champion_id = mastery["championId"]
                champion_level = mastery["championLevel"]
                champion_points = mastery["championPoints"]
                
                champion_name = champion_ids.get(champion_id, f"Чемпион {champion_id}")
                
                mastery_table.append([f"{champion_name}", champion_id, champion_level, champion_points])
            
            mastery_table_text = tabulate(mastery_table, headers=["Ник Чемпиона", "ID", "Уровень мастерства", "Очки мастерства"], tablefmt="grid")
            stat_text += f"\n{mastery_table_text}"
        else:
            stat_text += "Призыватель не имеет информации о мастерстве.\n"
        
        # Записываем всю статистику в файл
        with open("stat.txt", "w") as stat_file:
            stat_file.write(stat_text)
        
        print("Статистика сохранена в файл stat.txt")
    else:
        print(f"Произошла ошибка при запросе. Код ошибки: {rank_response.status_code}")
else:
    print(f"Произошла ошибка при запросе. Код ошибки: {summoner_response.status_code}")