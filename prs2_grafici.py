'''
Autore: Stefano Sambo
Ultimo aggiornamento: 14/01/25
Descrizione: Funzioni volte alla creazione di grafici'''

import altair as alt
import polars as pl
import prs2_dataset as ds
import pandas as pd


#FUNZIONA
#ritorna il grafico delle percentuali di tiro secondo le sequenze dei tiri precedenti
def sequence_graph(df):  #df:seqdf -> graph: sequencesfgs
    #assegno il valore dell'ascisse a seconda della lunghezza della sequenza
    df = df.with_columns(
        pl.when(pl.col("Sequence") == "1st").then(0)  #se da Sequence ricava 1st -> primo tiro -> 0
        .when(pl.col("Sequence").is_in(["C", "E"])).then(1)  #altrimenti=lunghezza sequenza
        .when(pl.col("Sequence").is_in(["CC", "EE", "CE", "EC"])).then(2)
        .when(pl.col("Sequence").is_in(["CCC", "CCE", "CEC", "CEE", "ECC", "ECE", "EEC", "EEE"])).then(3)
        .alias("X")
    )

    df = df.with_columns(
        pl.when(pl.col("Sequence").str.slice(-1) == "C").then(pl.lit("#6A0DAD"))  #canestri = viola 
        .when(pl.col("Sequence").str.slice(-1) == "E").then(pl.lit("#9E9AC8"))  #errori = lilla  
        .when(pl.col("Sequence") == "1st").then(pl.lit("white"))  #per 1st
        .otherwise(pl.lit("gray"))  #per evitare errori
        .alias("Color")
    )

    #dato che il valore dell'ordinata è in base alla fg%, cambio il df in modo che escluda le caselle dove il calcolo di fg% restituisce None
    df_filtered = df.filter(pl.col("FG%").is_not_null())

    #grafico vero e proprio
    chart = alt.Chart(df_filtered.to_pandas()).mark_circle(size=50).encode(
        x=alt.X("X:O", title="Numero di tiri precedenti",
                scale=alt.Scale(domain=[0, 1, 2, 3]),  #richiamo i valori definiti prima dell'ascisse 
                axis=alt.Axis(labels=True)), 
        y=alt.Y("FG%:Q", title="FG%", scale=alt.Scale(domain=[0, 100])),  #essendo una percentuale, voglio che vari da 0 a 100
        color=alt.Color("Color:N", 
            legend=alt.Legend(
                title="Dopo un",  #il colore rappresenta l'esito del tiro precedente -> "dopo un"
                orient="right",  #per evitare che vada in mezzo al grafico
                labelExpr="datum.label === '#6A0DAD' ? 'Canestro' : datum.label === '#9E9AC8' ? 'Errore' : 'Primo tiro'"
            ),
            scale=alt.Scale(domain=["#6A0DAD", "#9E9AC8", "white"], range=["#6A0DAD", "#9E9AC8", "white"])  

        ),
        tooltip=["Sequence", "FG%"]
    ).properties(
        title=f"FG% in base alle sequenze di tiro precedenti",
        width=800  #lunghezza impostata manualmente
    ).interactive()  

    return chart

#FUNZIONA
#ritorna il grafico della percentuale cumulativa di un giocatore durante la singola partita
def singlegame_fg_graph(modified_events):  #list:events -> graph:shotsgraph
    #se len=0 significa che il giocatore non ha tirato -> non restituisco niente
    if len(modified_events) == 0:
        return None

    #imposto le variabili per tracciare le fg cumulative
    makes = 0
    total_shots = 0
    fg_percentages = []

    for _, event in enumerate(modified_events):
        if event == "C":
            makes += 1
            color = "#6A0DAD"  #canestri = viola 
        elif event == "E":
            color = "#9E9AC8"  #errori = lilla
        total_shots += 1
        fg_percentage = (makes / total_shots) * 100  #per ogni tiro la fg cambia, quindi vado a calcolarla
        fg_percentages.append({"Shot Number": total_shots, "FG%": fg_percentage, "Color": color})  #imposto i valori per dopo

    df = pd.DataFrame(fg_percentages)  #per comodità, direttamente da pandas

    #comincio a impostare il grafico
    graph = alt.Chart(df).mark_circle(size=50).encode(
        x=alt.X(
            "Shot Number:Q",
            title="Numero cumulativo di Tiri",
            axis=alt.Axis(values=list(range(1, len(modified_events) + 1)), tickMinStep=1)  #voglio che si vedano tutte le unità, quindi tutti i tiri
        ),
        y=alt.Y(
            "FG%:Q",
            title="FG% Cumulativa",
            scale=alt.Scale(domain=[0, 100]),  #stesso discorso della funzione precedente
            axis=alt.Axis(format=".0f") 
        ),
        color=alt.Color(  #imposto i colori
            "Color:N", 
            scale=alt.Scale(
                domain=["#6A0DAD", "#9E9AC8"],
                range=["#6A0DAD", "#9E9AC8"]
            ),
            legend=alt.Legend(
                title="Esito del Tiro",
                orient="right",
                labelExpr="datum.label === '#6A0DAD' ? 'Canestro' : 'Errore'"  #viola associato ai make, il lilla ai miss
            )
        ),
        tooltip=["Shot Number", "FG%"]
    ).properties(
        width=800,
        height=400
    ).interactive()  

    return graph

#FUNZIONA
#ritorna il grafico della serie storica delle statistiche generali partita per partita
def gameforgame_stats_graph(player_name):  #str:name -> graph:sumupgraph
    game_numbers = []
    c_counts = []
    e_counts = []
    streak_counts = []  #imposto le liste per le statistiche

    games = ds.player_gamelogs_df(player_name)
    if games is None:
        return None  #check se il nome c'è nel database
    
    gamecounter = 0  #imposto il counter
    for _, game in games.iterrows(): 
        game_id = game["Game_ID"]
        filtered_events = ds.player_modifiedevents_list(game_id, player_name)

        C_count, E_count, streak_count, useless_fg = ds.single_game_stats(filtered_events)

        gamecounter += 1  #aggiornato per ogni partita
        game_numbers.append(gamecounter)  
        c_counts.append(C_count)
        e_counts.append(E_count)
        streak_counts.append(streak_count)

    statsdata = pd.DataFrame({
        "Game Number": game_numbers,
        "Canestri": c_counts,
        "Errori": e_counts,
        "Streaks": streak_counts
    })

    #trasformazione per compatibilità con altair
    long_data = statsdata.melt(
        id_vars="Game Number",
        var_name="Metric",
        value_name="Value"
    )

    #grafico
    chart = alt.Chart(long_data).mark_line(point=True, strokeWidth=1).encode(
        x=alt.X(
            "Game Number:Q", 
            title="Numero della Partita",
            scale=alt.Scale(domain=[1, len(game_numbers)], nice=False),  #per mostrare tutti gli interi
            axis=alt.Axis(values=list(range(1, len(game_numbers) + 1)))  
        ),
        y=alt.Y(
            "Value:Q", 
            title="Valore"
        ),
        color=alt.Color(
            "Metric:N", 
            scale=alt.Scale(domain=["Canestri", "Errori", "Streaks"],
                            range=["#6A0DAD", "#9E9AC8", "#FC9272"]),  #canestri=viola , errori=lilla, streaks=arancione
            legend=alt.Legend(title="Statistiche", orient="right") 
        ),
        tooltip=["Game Number", "Metric", "Value"]
    ).properties(
        title=f"Andamento delle Statistiche partita per partita: {player_name}",
        width=800,
        height=400
    ).interactive()

    return chart

#FUNZIONA
#grafico della top 5 (già aggiornato)
def top5_graph(data): #list:data -> graph:top5graph
    df = pd.DataFrame(data, columns=['Giocatore', 'Canestri', 'Errori', 'Streaks'])
    
    df_long = df.melt(id_vars='Giocatore', 
                      var_name='Stats', 
                      value_name='Value')
    
    color_scale = alt.Scale(
        domain=["Canestri", "Errori", "Streaks"],
        range=["#6A0DAD", "#9E9AC8", "#FC9272"]  #viola , lilla, arancione  
    )
    
    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X("Giocatore:N", title="Giocatore", axis=alt.Axis(labelAngle=0)),  
        y=alt.Y("Value:Q", title="Value"),                                 
        color=alt.Color("Stats:N", scale=color_scale, title="Stats"), 
        xOffset="Stats:N"  #mette a fianco le barre in base alla categoria
    ).properties(
        width=300,  
        height=400 #userò use_container_width, non dovrebbero servire
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=15,
    ).configure_legend(
        titleFontSize=15,
        labelFontSize=12
    )
    
    return chart


