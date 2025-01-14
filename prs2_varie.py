'''
Autore: Stefano Sambo
Ultimo aggiornamento: 14/01/25
Descrizione: Funzioni che non sono ne estrazione dataset ne creazione di grafici'''


import prs2_dataset as ds
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import leaguedashplayerstats

#FUNZIONA, MA PER ORA INUTILE, VEDERE IN CORSO D'OPERA SE CON MODIFICHE SI PUO' PRESENTARE IN AGGIUNTA
def collect_all_games(player_name): 
    games = ds.player_gamelogs_df(player_name)
    all_game_events = []
    for _, game in games.iterrows():
        game_id = game["Game_ID"]
        game_events = ds.player_modifiedevents_list(game_id, player_name)
        all_game_events.append(game_events)
    return all_game_events

#FUNZIONA
#ritorna l'url della foto di un giocatore
def show_player_photo(player_name): #str:name->str:url
    player_id=ds.playerid_str(player_name)
    img_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
    return img_url


#FUNZIONA
#ritorna i nomi dei 5 giocatori con la media punti più alta, quindi i più rappresentativi per la nostra analisi
def get_top_scorers_names(): # ->list:topscorers
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season='2024-25').get_data_frames()[0] #recupera i giocatori con le rispettive statistiche in un df
    sorted_stats = stats.sort_values('PTS', ascending=False).head(5) #ordina il df per media punti e ne prende solo i primi 5 

    top_scorers = []
    for _, row in sorted_stats.iterrows(): #per ogni riga recupera il nome del giocatore e lo inserisce nella lista
        player_name = row["PLAYER_NAME"]
        top_scorers.append(player_name)

    return top_scorers


