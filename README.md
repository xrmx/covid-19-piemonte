
<hr>

# Scopo del repository

Lo scopo del repository è di raccogliere informazione sulla pandemia del Coronavirus in Piemonte, utilizzando di preferenza i dati resi disponibili dagli enti pubblici regionali
.
# Nota

Questo repository diventerebbe in parte o in toto superfluo qualora gli enti pubblici piemontesi rilasciassero i dati relativi alla pandemia in formato aperto, cioè:
in formato ***machine readable***, con **licenza aperta**, certificati, **completi**, il più possibile **disaggregati**, **aggiornati** e con lo **storico** dei dati nel tempo.

# Programmi disponibili

## Scaricamento dei dati dal sito della Regione Piemonte in formato aperto csv
Dal 10 aprile (o anche da qualche giorno prima, non sono certo di questa data) la Regione Piemonte pubblica sulla pagina

[https://www.regione.piemonte.it/web/covid-19-mappa-dei-contagi-piemonte](https://www.regione.piemonte.it/web/covid-19-mappa-dei-contagi-piemonte)

una mappa coropletica con il numero dei positivi per comune. Muovendo il mouse sulla mappa, è visualizzato il numero di positivi per il comune corrispondente alla data di aggiornamento della mappa.

Visto che è impensabile portare il mouse su ognuno dei 1180 circa comuni piemontesi per ottenere il dato dei positivi in tutti i comuni della regione, il programma

scarica_dati_da_regione_piemonte.py

utilizza il pacchetto Selenium per richiedere la pagina contenente la mappa al sito della Regione Piemonte come un qualsiasi web browser e per accedere alla struttura javascript che conserva i dati dei positivi per comune. Questi dati sono salvati in un file csv nella sottocartella data.

## Aggregazione di tutti i dati in unico file
A partire dal giorno 10 maggio 2020 è caricato nella cartella data un file in formato CSV con nome

con tutti i dati disponibili dal 25 marzo 2020 fino alla data indicata nel nome del file.

Sono inoltre presenti i dati aggregati per provincia, intera regione e ASL.

Mancano i dati del 10 e 11 aprile 2020.

La tabella seguente elenca le colonne del file con la loro descrizione
&nbsp;

&nbsp;


| Nome colonna             | Descrizione |
|--------------------------|-------------|
| Ente | Nome comune, ASL, provincia, regione |
| Tipo	 | Tipo ente, ASL o COM o PRO o REG |
| Provincia	 | Provincia, non significativo per ASL |
| ASL	 | ASL, non significativo per provincia e regione |
| Codice ISTAT	 | codice ISTAT o codice azienda ASL (*) |
| Abitanti	 | numero abitanti |
| Positivi	 | numero positivi al Covid-19 |
| Positivi 1000 abitanti	 | numero positivi al Covid-19 per 1000 abitanti |
| Delta positivi	 | differenza positivi rispetto al giorno precedente |
| Delta positivi 1000 abitanti	 | differenza positivi per 1000 abitanti rispetto al giorno precedente |
| Data | data in formato aaaa/mm/gg |

(\*) Per evitare possibili collisioni tra i codici ISTAT di comuni, province e regione e i codici azienda della ASL,
a questi ultimi è stato aggiunto il prefisso 'A'


## Conversione dei dati aggregati dei contagi nelle RSA in formato aperto csv

Il 15 aprile 2020 la Regione Piemonte ha pubblicato un file PDF

[https://www.regione.piemonte.it/web/sites/default/files/media/documenti/2020-04/tabelle.pdf](https://www.regione.piemonte.it/web/sites/default/files/media/documenti/2020-04/tabelle.pdf)

con tre tabelle che riassumevano gli esiti aggregate per ASL dei tamponi nelle RSA ai giorni 8 e 14 aprile e un confronto dei dati di mortalità tra 2019 e 2020. Le tabelle sono in formato immagine e non testuale e annegate in un file pdf.

I file csv

- RSA-tamponi-04-08.csv
- RSA-tamponi-04-14.csv
- RSA-deceduti.csv

presenti nella sottocartella data contengono i dati delle tabelle nel file tabelle.pdf.

## Tentativo di analisi di maggior dettaglio dei contagi nelle RSA

La Regione Piemonte ha fornito i dati relativi ai contagi nelle RSA aggregandoli a livello di ASL (vedi paragrafo precedente), rendendo difficile se non impossibile individuare in quali comuni sia presente il problema di focolai di infezione tra gli ospiti e il personale delle RSA.

Due programmi sono a disposizione per cercare degli indizi indiretti di queste situazioni. E' importante osservare che si tratta di indizi da verificare e non di prove certe che confermino la presenza di focolai infettivi nelle RSA presenti in un certo comune.

### Positivi per 1000 abitanti

Il programma

ordina_per_positivi_su_1000_abitanti.py

ha come input un qualsiasi file con il numero di positivi per tutti i comuni piemontesi prodotto dal programma scarica_dati_da_regione_piemonte.py, calcola ove già non disponibile il numero di positivi per 1000 abitanti e ordina i comuni del Piemonte in modo discendente in base a tale dato.

Emerge che i comuni con la maggiore densità di infezione sono nella stragrande maggioranza dei casi quelli con meno abitanti (meno di 10000) e si ipotizza che questa densità possa essere dovuta alla presenza nel territorio comunale di una RSA focolaio di infezione. Si ripete che questo è un indizio da verificare, non una prova certa, anche se vi sono notizie di stampa che confermano l'esistenza del problema in molti (molti, non tutti) dei comuni in testa alla lista. Peraltro il comune con il numero più elevato di positivi, cioè Chialamberto, non sembra avere problemi di RSA, perlomeno in base a quanto risulta da una ricerca su internet.

E' utile osservare che questo metodo vale per comuni con popolazione più numerosa, perché in questo caso gli effetti della presenza di una o anche poche RSA focolai di infezione sarebbero diluiti dalla popolazione del comune.

### Anomalo incremento del numero di positivi

Il programma

evidenzia_incrementi_anomali_positivi.py

esamina per ogni comune il numero di contagi nelle ultime due settimane e evidenzia i casi in cui si riscontri un incremento del numero dei positivi superiore a un certa percentuale rispetto al giorno precedente. L'ipotesi è che questi incrementi anomali possano derivare dalla pubblicazione dei risultati dei tamponi effettuati in RSA con molti positivi tra ospiti e personale della struttura. Anche in questo caso si tratta di indizi da verificare e non di una prova.

# Dati

I programmi sopra illustrati leggono e scrivono file nella sottocartella data

| Contenuto | Nome file |
| --- | --- |
| Positivi per comune da Regione Piemonte | dati_aaaa_mm_gg_da_regione_piemonte.csv (1)|
| Comuni ordinati per positivi / 1000 abitanti | comuni_ordinati_per_densita_contagio_2020_mese_giorno.csv |
| Incrementi numero anomali | positivi incrementi_positivi_anomali_2020_mese_giorno.csv |
| Aggregazione di tutti i dati in un unico file | dati_per_tutto_il_periodo_aaaa_mm_gg.csv |


(1) Il file dati_2020_04_09_da_regione_piemonte.csv contiene i dati dal 25 marzo al 9 aprile compresi. Mancano i file relativi ai giorni 10 e 11 aprile


# Licenza

I programmi sono disponibili secondo i criteri della licenza MIT

I dati originali sono forniti dalla Regione Piemonte e da altri enti pubblici piemontesi e pubblicati sui rispettivi siti istituzionali.
Qualora la Regione Piemonte o un altro ente ritenga che la pubblicazione di questi dati in formato aperto costituisca una violazione di qualche Copyright detenuto dall'ente stesso, i dati verranno rimossi da questo repository su richiesta del detentore di tali diritti.
