# prog_sambostefano
INTRODUZIONE GENERALE
Il progetto va ad effettuare un'indagine statistica su alcuni dati relativi alle partite della NBA, ossia la massima lega di pallacanestro americana e mondiale.
In particolare, oltre a dare una panoramica generale sulle statistiche generali del giocatore, si analizzano le percentuali di successo di un tiro condizionate agli
esiti precedenti, in modo da poter confermare o confutare la tesi dell'effetto della "mano calda e mano fredda", secondo la quale tali esiti precedenti hanno un
importante influenza sulle percentuali di successo.

STRUTTURA DEL PROGETTO: CODICE
Il codice è stato diviso in 4 sezioni, ognuna riferita allo scopo delle funzioni e delle righe scritte all'interno.
La prima sezione è "dataset", che include tutte le funzioni necessarie per ricavare ogni tipo di dato utile all'applicazione. Per questo lavoro è stata 
fondamentale la libreria nba_api, che permette non solo di ricavare tutte le informazioni di ogni giocatore e squadra ma anche, partendo dagli id delle partite 
singole, tutti i  logs delle partite: questi dataset non sono altro che un elenco di ogni singolo evento accaduto durante la partita (tra i 500 e i 750), con una 
mole considerevole di variabili per ogni evento. La maggior parte delle funzioni della sezione si occupa quindi di prendere i singoli log e ricavarne solo gli 
eventi desiderati che, essendo un analisi sulle percentuali di tiro, sono appunto tutti i tiri presi dal campo, per giocatore e per esito. In particolare, sono 
stati ricavati:
- i canestri, ossia gli esiti positivi, individuati come C o Makes;
- gli errori, ossia gli esiti negativi, E o Misses.
Partendo da questi, si sono anche ricavate le streaks (strisce di 3 esiti consecutivi uguali) e, sopratutto, la percentuale di successo cercata (la FG%, per field
goal percentage), ossia N°canestri/(N°canestri + N°errori): combinando questa alle sequenze di esiti precedenti (fino a un massimo di 3), usando la formula della
probabilità condizionata P(successo|condizione)=P(successo ∩ condizione)/P(condizione), si sono trovate le singole probabilità condizionate ad ogni sequenza di
esiti possibile.
Ci sono inoltre funzioni per ricavare le statistiche medie per partita, per poter fare un confronto con i casi singoli.
La seconda sezione è "grafici", che include appunto tutte le funzioni dedite alla creazione di grafici tramite Altair, usando i dati ricavati dalla prima sezione.
Oltre a un grafico a barre per confrontare più giocatori e un grafico a dispersione che mostra tutte le probabilità condizionate, ci sono 2 serie storiche di certe
statistiche, una che usa le partite come unità temporale per mostrare l'andamento delle statistiche generali, mentre l'altra mostra l'andamento della percentuale
di una partita tiro per tiro di un certo giocatore.
La terza è "varie", alla quale appartengono tutte le funzioni che non appartengono a nessuna delle 2 sezioni precedenti.
L'ultima è "streamlit", che è il codice dell'applicazione vera e propria, che sfrutta gli import di tutte le altre funzioni per generare i dataset e i grafici
tramite gli input dell'utente.
Il codice è stato fatto in modo che i dataset siano non fissi, ma che possano mutare nel tempo: grazie alla libreria nba_api infatti i dati vengono constantemente
aggiornati, quindi se il codice viene fatto partire in 2 momenti diversi e in mezzo a questi c'è stata una partita, i risultati saranno diversi.

STRUTTURA DEL PROGETTO: APPLICAZIONE
Tolta la home, anche l'applicazione è stata divisa in 4 sezioni, che però ovviamente non sono collegate a una a una con le sezioni del codice.
La prima è un'introduzione, che serve a spiegare agli utenti meno esperti dell'argomento di cosa si tratta e cosa fa l'applicazione.
La seconda è "percentuali condizionate" che, come intuibile dal titolo, effettua l'analisi delle probabilità condizionate dalle singole sequenze.
La terza è "statistiche generali" che introduce le streaks e da una panoramica sulle statistiche generali del giocatore, oltre che un pulsante che se premuto va a 
generare il grafico dell'andamento della percentuale partita per partita.
L'applicazione è strutturata in modo che vada a ricavare dataset e generare grafici per i giocatori richiesti dall'utente. C'è quindi un text_input dove l'utente 
inserisce il nome del giocatore desiderato e premendo invio partono tutte le funzioni che vanno a comporre la pagina. Sono anche elencati 5 nomi di alcuni giocatori
abbastanza famosi, nel caso in cui l'utente non sappia chi inserire.
La quarta e ultima è "statistiche top 5", che illustra le statistiche dell'ultima partita giocata dai 5 migliori giocatori della lega per media punti: si è scelta
tale statistica poichè spesso i giocatori che fanno più punti sono quelli che tirano di più, sono quindi ottimi da inserire nelle pagine precedenti come input per 
avere una grande quantità di dati da analizzare.
Ulteriori spiegazioni dei dati e dei grafici mostrati sono presenti nelle singole pagine, in modo che siano disponibili anche all'utente.

SCOPO DEL PROGETTO
Come accennato nell'introduzione generale, lo scopo del progetto era di verificare il mito della mano calda e mano fredda, ossia vedere se una sequenza di esiti
positivi antecedente a un tiro ne influenzasse positivamente la probabilità di successo e, viceversa, se una sequenza di esiti negativi lo influenzasse 
negativamente. Anche se è l'utente che, tramite i suoi input e gli strumenti dell'applicazione, può scoprirlo autonomamente bastano alcuni test con vari giocatori 
di varia importanza per verificare che il mito è molto facile da sfatare: quasi mai vi è una correlazione precisa, addirittura a volte gli esiti positivi hanno 
influenza negativa e gli esiti negativi hanno influenza positiva. Il mito è quindi fasullo e, essendo globalmente diviso da molti giocatori e appassionati di
pallacanestro, è un risultato molto particolare.
L'applicazione è anche pensata per un eventuale uso da parte degli allenatori. Ormai il basket è uno sport dove la statistica svolge un ruolo fondamentale 
(basti pensare all'uso del tiro da 3 punti, conclusione particolare ormai abusata semplicemente perchè è quella col valore atteso più alto) e gli staff tecnici 
sono sempre alla ricerca di nuovi dati da analizzare e sfruttare a proprio vantaggio. Avendo a disposizione tutte le percentuali condizionate possono scegliere 
quale giocatore far tirare in determinate situazioni: se, per esempio, un giocatore ha un'alta percentuale di successo dopo un errore, può essere che sfruttino la 
cosa per prediligere un suo tiro in quella situazione.

FONTI DI DATI
La fonte dei dati sono appunto i gamelogs messi a disposizione da nba_api, che elencano tutti gli eventi di tutte le partite di una certa stagione in modo che 
siano facili da sfruttare per creare funzioni tipo quelle di "dataset". In alternativa sono visualizzabili in modo molto più user-friendly sul sito ufficiale dell 
NBA "nba.com", ma non sono presenti analisi o approfondimenti come quelli svolti dall'applicazione.

APPROFONDIMENTI FUTURI
Durante la realizzazione del progetto mi è capitato di leggere un capitolo di "Cognitive Psychology" di Thomas Gilovich, psicologo e professore alla Cornell 
University che, proprio in quel capitolo, fu uno dei primi a confutare il mito della mano calda (defindendolo una "cognitive illusion"), usando i metodi statistici 
dell'epoca (il libro uscì nel 1985) e usando dei dati riferiti alla stagione del 1980-81. Ho deciso quindi, come probabile progetto di tesi, di approfondire le
analisi statistiche effettuate da Gilovich, andando a creare un modello statistico sui dataset ricavati proprio con le funzioni di questo progetto, per verificare 
se si arriva alle stesse conclusioni alle quali lo psicologo arrivò 40 anni fa.
