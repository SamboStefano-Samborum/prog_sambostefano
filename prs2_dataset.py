'''
Autore: Stefano Sambo
Ultimo aggiornamento: 14/01/25
Descrizione: file raccolta funzioni di estrazioni dataset, sia per le sequenze condizionate che per dati partita per partita'''



import re
from nba_api.live.nba.endpoints import playbyplay
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import polars as pl


#FUNZIONA
#ritorna la lista completa degli eventi di una partita sotto forma di dizionario
def playbyplay_dict(game_id): #str:id -> dict:pbpdata
    pbp_data = playbyplay.PlayByPlay(game_id=game_id, timeout=300).get_dict() #usa la funzione dell'api
    return pbp_data

#FUNZIONA
#ritorna la lista modificata di C ed E per l'analisi delle sequenze
def player_modifiedevents_list(game_id, player_name): #str:id, str:name -> list: events
    modified_events = [] #imposto la lista vuota
    player_name_and_surname = player_name.split() #dato che nel database players compaiono nome e cognome intero ma nella partita solo nel cognome, splitto nome e cognome
    player_name = player_name_and_surname[-1]  #considero solo l'ultima parte della stringa, ossia il cognome, in modo da riconoscerlo nella partita, si chiama player_name e non surname per comodità
    ast_string = re.compile(rf"{re.escape(player_name)}\s+\d+\s+AST")  #l'evento AST è scomodo, perchè compare il nome del giocatore pur non essendo un suo tiro, ne individuo quindi la stringa associata

    pbp_data = playbyplay_dict(game_id) #uso la funzione sopra

    for event in pbp_data["game"]["actions"]:
        eventdesc = event["description"] #per ogni evento individuo la description, cioè ciò che mi interessa

        if "free throw" in eventdesc.lower(): #se è un free throw non rientra nelle percentuali di tiro
            continue  #quindi lo escludo

        #cerco gli eventi dove compare il nome del giocatore, escludendone gli assist via il pattern
        if player_name.lower() in eventdesc.lower() and not ast_string.search(eventdesc):
            if "MISS" in eventdesc: #=tiro sbagliato, quindi mi interessa
                eventdesc = "E"  #E=errore
            elif "PTS" in eventdesc: #e non è un free throw = tiro segnato, quindi mi interessa
                eventdesc = "C"  #C=canestro
            else:
                continue  #altri eventi che possono essere rebound, turnover ecc. non mi interessano

            modified_events.append(eventdesc)  #aggiungo la description, quindi C o E, alla lista eventi

    return modified_events

#FUNZIONA
#ritorna il numero di streaks in una partita
def streaknumber_int(modified_events): #list:events -> int:streaks
    if len(modified_events) < 3:
        return 0  #se la lista ha meno di 3 elementi significa che il giocatore ha tirato meno di 3 volte, quindi non può avere completato una streak 
    streak_count = 0  #imposto il counter
    for i in range(len(modified_events) - 2):  #scorro la lista
        if modified_events[i] == modified_events[i + 1] == modified_events[i + 2]: #se per ogni elemento i successivi 2 sono uguali -> streak
            streak_count += 1
#DISCLAIMER: la definizione di "streaky shooter" si applica sia a canestri che a errori consecutivi, perciò non mi interessa dividere le 2 cose
    return streak_count
    
#FUNZIONA
#ritorna l'id di un giocatore partendo dal nome, utile perchè molte funzioni dell'api usano l'id
def playerid_str(player_name): #str:name -> str:id
    players_dict = players.get_players() #ricavato con l'api
    player = next((plr for plr in players_dict if plr["full_name"].lower() == player_name.lower()), None) #cerco nel players_dict il giocatore che corrisponde al nome inserito
    if player:
        return player["id"] #se c'è lo ritorno
    else:
        return None #altrimenti non ritorno niente

#FUNZIONA 
#ritorna un df con tutte le partite di tale giocatore, utile per visualizzazione e per ricavare l'id partita
def player_gamelogs_df(player_name): #str:name -> df:games
    player_id = playerid_str(player_name) #richiesto l'id
    if not player_id: #se non c'è
        return None #non ritorno niente
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, timeout=300) #avendo l'id, posso individuare tutte le partite dove compare tale giocatore, timeout a 300 perchè per giocatori con dataset più pesanti quello di default va in errore
    gamelogs = gamelog.get_data_frames()[0]
    gamelogs=gamelogs[::-1] #dato che i logs partono dalla partita più recente, inverto l'order
    return gamelogs



#FUNZIONA
#imposta il df vuoto per la tabella delle sequenze
def emptytable_df(): # -> df:emptytable
    rowsandcolumns = {
    "Sequence": [
        "1st", "C", "E", "CC", "CE", "EC", "EE", 
        "CCC", "CCE", "CEC", "CEE", "ECC", "ECE", "EEC", "EEE" #righe vuote
    ], #=esiti precedenti
    "C": [0] * 15,
    "E": [0] * 15,
    "FG%": [None] * 15 #colonne vuote
    }
    df = pl.DataFrame(rowsandcolumns)
    return df

#FUNZIONA
#ritorna il df aggiornato, usando gli eventi della lista modificata
def events_updated_df(event_list, df): #list:event, df:df -> df:updateddf
    previous_events = [] #lista per tracciare gli esiti precedenti

    for event in event_list:
        row_name = "".join(previous_events) if previous_events else "1st" #si determina la riga in base a previous_events, se vuoto->è il primo->1st

        #aggiorniamo il df con l'aggiunta alla colonna giusta
        df = df.with_columns(
            pl.when(pl.col("Sequence") == row_name) #se c'è un evento associato
            .then(pl.col(event) + 1) #+1 alla casella desiderata
            .otherwise(pl.col(event)) #altrimenti niente
            .alias(event)
        )

        previous_events.append(event) #aggiungiamo l'evento alla lista degli eventi precedenti
        if len(previous_events) > 3:
            previous_events.pop(0)  #non appena la lista supera i 3 eventi togliamo quello più lontano

    return df



#FUNZIONA
#ritorna il df totale delle sequenze
def updated_player_events_df(player_name): #str:name -> df:eventsdf
    df = emptytable_df()
    games = player_gamelogs_df(player_name)
    if games is None: #!!!perché if not games non va?!!!
        return None

    for _, game in games.iterrows(): #per ogni partita 
        game_id = game["Game_ID"] #ricava l'id
        game_events = player_modifiedevents_list(game_id, player_name) #va a ricavare gli eventi
        df = events_updated_df(game_events, df) #e ci aggiorna il df

    df = df.with_columns( 
        pl.when((pl.col("C") + pl.col("E")) >= 5)
        .then((pl.col("C") / (pl.col("C") + pl.col("E")) * 100).round(2))
        .otherwise(None)
        .alias("FG%")
    ) #una volta raccolti tutti i dati, va a calcolare la percentuale di canestri nelle righe con almeno 5 tiri tentati (meno sono un dato poco rappresentativo)

    return df

#FUNZIONA
#ritorna le sequenze dei valori massimi o minimi di fg%
def max_min_fg(df):  #df: df -> str: seqs and fgs
    valid_fg_df = df.filter(pl.col("FG%").is_not_null())

    if valid_fg_df.is_empty():
        return None, None, None, None  #expection extra in caso di df vuoto

    max_fg_row = valid_fg_df.sort("FG%", descending=True).row(0) #mette in ordine decrescente il df rispetto alla fg, poi prende la prima riga
    max_sequence = max_fg_row[0]  
    max_fg = max_fg_row[3]       

    
    min_fg_row = valid_fg_df.sort("FG%").row(0) #analogo, ma ordine crescente
    min_sequence = min_fg_row[0] 
    min_fg = min_fg_row[3]        

    return max_sequence, max_fg, min_sequence, min_fg

#FUNZIONA
#va a calcolare le singole statistiche di rilievo di una partita
def single_game_stats(filtered_events): #list:events -> ints:stats
    C_count = filtered_events.count("C") #conta gli eventi=C
    E_count = filtered_events.count("E") #stessa cosa per E
    streak_count = streaknumber_int(filtered_events) #usa la funzione per strovare le streaks

    if C_count + E_count > 0: #se la lista non è vuota va a calcolare la percentuale, altrimenti no
        fg_percentage = (C_count / (C_count + E_count)) * 100
    else:
        fg_percentage = None

    rounded_fg = round(fg_percentage, 1) if fg_percentage else None #la arrotondo
        
    return C_count, E_count, streak_count, rounded_fg

#FUNZIONA
#restituisce un df con le statistiche di tutte le singole partite
def total_stats_df(player_name): #id:name -> df:statsdf
    game_numbers = []
    makes = []
    misses = []
    streaks_list = []
    fg_percentages = []
    game_count=0 #imposto le liste vuote e un counter

    games = player_gamelogs_df(player_name)
    if games is None: #expection in caso non vengano i dati
        return None

    for _, game in games.iterrows():
        game_count += 1  #per ogni partita aggiorno il counter e vado a ricavarmi gli eventi
        game_id = game["Game_ID"]
        game_events = player_modifiedevents_list(game_id, player_name)

        C, E, streaks, fg = single_game_stats(game_events) #dagli eventi ricavo le statistiche

        game_numbers.append(f"N.{game_count}") #e le inserisco nelle liste
        makes.append(C)
        misses.append(E)
        streaks_list.append((streaks))
        fg_percentages.append(fg)

    #una volta fatte le liste, le uso per creare il df
    df = pl.DataFrame({  
        "Games": game_numbers,
        "Makes": makes,
        "Misses": misses,
        "Streaks": streaks_list,
        "FG%": fg_percentages
    })

    return df


#FUNZIONA
#ritorna le statistiche medie, quindi statistiche totali/partite
def summary_stats(df): #df:statsdf -> ints:avgstats
    if df is None or df.is_empty():
        return None
    
    #sommo tutti i dati del df per ottenere le somme totali
    total_makes = sum(df["Makes"])
    total_misses = sum(df["Misses"])
    total_streaks = sum(df["Streaks"])
    total_games = len(df["Games"])  #qua uso len
    
    #faccio le medie arrotondate
    makespg = round(total_makes / total_games, 2)
    missespg = round(total_misses / total_games, 2)
    streakspg = round(total_streaks / total_games, 2)
    if total_makes + total_misses > 0:
        totalfg = round((total_makes / (total_makes + total_misses)) * 100, 2)  #calcolo della percentuale totale
    else: totalfg = 0
    
    return makespg, missespg, streakspg, totalfg


#FUNZIONA
#resituisce il log dell'ultima partita giocata da un certo giocatore
def last_gamelog(player_name): #str:playername -> dict: log
    logs=player_gamelogs_df(player_name)
    if logs is None:
        return None
    df=pl.DataFrame(logs)
    return df.tail(1) #restituisco l'ultimo



