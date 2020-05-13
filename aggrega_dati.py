"""
questo programma
- carica i file con i dati relativi ai positivi al COVID 19
resi disponibili dalla Regione Piemonte
- calcola eventuali informazioni mancanti
- aggiungi le informazioni sulla ASL
- calcola popolazione e positivi 1000 abitanti per province, regione, ASL
- scrive un file con tutti i dati relativi a tutti i giorni disponibili
"""
from pathlib import Path
import pandas as pd

PROV = {"001": "TO", "002": "VC", "003": "NO", "004": "CN", "005": "AT",
        "006": "AL", "096": "BI", "103": "VCO"}

COD_PIEMONTE = '01'

COLONNE = ['Ente', 'Tipo', 'Provincia', 'Positivi',
           'Positivi 1000 abitanti',
           'Abitanti', 'Data', 'Codice ISTAT', 'ASL']

DESCRIZIONE_TIPO = {
    'ASL': 'ASL',
    'COM': 'comune',
    'PROV': 'provincia',
    'REG': 'regione',
}


def provincia(row):
    """
    ritorna provincia associata a codice ISTAT di comune
    """
    return PROV[str(row["Codice ISTAT"][:3])]


def aggrega_per_province(dfall, popolazione):
    """
    calcola somme per provincia e per intera regione
    """
    # positivi per provincia e per regione
    per_provincia = dfall.groupby(['Data', 'Provincia'],
                                  as_index=False).Positivi.sum()
    per_provincia['Tipo'] = 'PROV'
    per_regione = dfall.groupby(['Data'], as_index=False).Positivi.sum()
    per_regione['Provincia'] = "Piemonte"
    per_regione['Tipo'] = 'REG'
    per_regione = per_regione.reindex(columns=per_provincia.columns)
    # unisci dati per regione e per provincia
    somme = pd.concat([per_provincia, per_regione], axis=0)
    # sistema gli indici
    somme = somme.reset_index(drop=False)
    # calcola popolazione per provincia e per regione
    abitanti = popolazione.groupby(['Provincia'], as_index=False) \
        .Abitanti.sum()
    abitanti.loc[abitanti.shape[0]] = ['Piemonte', abitanti.Abitanti.sum()]
    # assegna abitanti a ogni riga per province e regione
    somme['Abitanti'] = 0
    for prov in PROV.values():
        num = int(abitanti[abitanti['Provincia'] == prov]['Abitanti'])
        somme.loc[somme['Provincia'] == prov, 'Abitanti'] = num
    num = int(abitanti[abitanti['Provincia'] == 'Piemonte']['Abitanti'])
    somme.loc[somme['Provincia'] == 'Piemonte', 'Abitanti'] = num
    # positivi 1000 abitanti
    somme['Positivi 1000 abitanti'] = ((1000 * somme['Positivi']) /
                                       somme['Abitanti']).round(2)
    # codice ISTAT
    somme['Codice ISTAT'] = ""
    somme.loc[somme['Provincia'] == 'Piemonte', 'Codice ISTAT'] = COD_PIEMONTE
    for code, prov in PROV.items():
        somme.loc[somme['Provincia'] == prov, 'Codice ISTAT'] = code
    somme['Ente'] = somme['Provincia']
    somme['ASL'] = ' '
    # ordina le colonne
    somme = somme.reindex(columns=COLONNE)
    # ritorna il dataset
    print("Righe per provincie e regione", somme.shape[0])
    return somme


def aggrega_per_asl(dfall, popolazione, asl):
    """
    calcola somme asl
    """
    sommario_asl = asl[['CODICE AZIENDA', 'DENOMINAZIONE AZIENDA']] \
        .drop_duplicates()

    # positivi per provincia e per regione
    per_asl = dfall.groupby(['Data', 'ASL'],
                            as_index=False).Positivi.sum()
    # popolazione per ogni ASL
    abitanti = popolazione.groupby(['ASL'],
                                   as_index=False).Abitanti.sum()

    # merge codice ISTAT e popolazione
    per_asl = pd.merge(per_asl, sommario_asl, left_on='ASL',
                       right_on='DENOMINAZIONE AZIENDA')
    per_asl = pd.merge(per_asl, abitanti, on='ASL')
    per_asl['Codice ISTAT'] = 'A' + per_asl['CODICE AZIENDA']
    per_asl.drop(['CODICE AZIENDA', 'DENOMINAZIONE AZIENDA'],
                 axis=1, inplace=True)

    # positivi 1000 abitanti
    per_asl['Positivi 1000 abitanti'] = ((1000 * per_asl['Positivi']) /
                                         per_asl['Abitanti']).round(2)
    per_asl['Ente'] = per_asl['ASL']
    per_asl['Tipo'] = 'ASL'
    per_asl['Provincia'] = "N/A"
    # ordina le colonne
    per_asl = per_asl.reindex(columns=COLONNE)
    # ritorna il dataset
    print("Righe per ASL", per_asl.shape[0])
    return per_asl, sommario_asl


def carica_asl():
    """
    carica file csv con associazione comune - asl da Ministero Sanità
    http://www.dati.salute.gov.it/dati/dettaglioDataset.jsp?menu=dati&idPag=3
    aggiungi i nuovi comuni creati nel 2019
    """
    colonne = ['CODICE AZIENDA', 'DENOMINAZIONE AZIENDA', 'CODICE COMUNE']
    ifile = Path("data") / ("asl_piemonte.csv")
    asl = pd.read_csv(ifile, sep=";",
                      dtype={"CODICE COMUNE": "string",
                             "CODICE AZIENDA": "string"},
                      usecols=colonne)
    return asl


def aggiungi_delta_positivi(dfall, prima_data):
    # aggiungi in ogni riga la differenza in positivi su 1000 abitanti
    # rispetto al giorno Precedente
    dfall['Precedente'] = 0
    dfall['Delta'] = 0
    # usa shift per salvare il valore del giorno precedente
    dfall['Precedente'] = dfall['Positivi 1000 abitanti'].shift(1)
    # per il primo giorno assumi valore giorno precedente = valore attuale
    dfall.loc[dfall['Data'] == prima_data, 'Precedente'] = \
        dfall.loc[dfall['Data'] == prima_data, 'Positivi 1000 abitanti']
    dfall['Delta'] = (dfall['Positivi 1000 abitanti'] -
                      dfall['Precedente']).round(2)
    dfall.drop(['Precedente'], axis=1, inplace=True)
    return dfall


def carica_dati_da_regione_piemonte():
    """
    carica i dati dei positivi dai file scaricati dal sito della Regione
    """
    # elenco dei file csv con i dati dei positivi
    # ifiles = sorted(glob.glob("data/dati*.csv"))
    ifiles = sorted(Path('data').glob("dati*_da_regione_piemonte.csv"))
    # il primo file ha anche le informazione sul numero abitanti per comune
    print(ifiles[0])
    dfall = pd.read_csv(ifiles[0], sep=";",
                        dtype={"Codice ISTAT": "string"})

    # carica i file con i dati
    for ifile in ifiles[1:]:
        print(ifile)
        df1 = pd.read_csv(ifile, sep=";",
                          dtype={"Codice ISTAT": "string"})
        dfall = pd.concat([dfall, df1], axis=0)
        del df1
    print("Numero righe comuni ", dfall.shape[0])

    # tipo ente è comune
    dfall['Tipo'] = 'COM'

    # aggiungi la provincia
    dfall['Provincia'] = dfall.apply(provincia, axis=1)

    # rinomina colonna Comune
    dfall.rename({'Comune': 'Ente'}, axis=1, inplace=True)
    return dfall


def main():
    """
    aggrega i dati in un unico file
    """
    # opzione da definire per evitare noiosi messaggi di errore
    pd.set_option('mode.chained_assignment', None)

    dfall = carica_dati_da_regione_piemonte()

    # carica i dati delle ASL
    asl = carica_asl()
    # aggiungi i codici ASL ai dati per comune
    dfall = pd.merge(dfall, asl, left_on="Codice ISTAT",
                     right_on="CODICE COMUNE")
    dfall['ASL'] = dfall['DENOMINAZIONE AZIENDA']
    # rimuovi le colonne non utili
    dfall.drop(['CODICE AZIENDA', 'CODICE COMUNE', 'DENOMINAZIONE AZIENDA'],
               axis=1, inplace=True)
    print("Numero righe comuni con ASL", dfall.shape[0])

    # ottieni popolazione
    prima_data = dfall['Data'].min()
    col_pop = ['Abitanti', 'Codice ISTAT', 'Provincia', 'ASL']
    popolazione = dfall[dfall['Data'] == prima_data][col_pop].reset_index()

    # merge dataset con popolazione per avere numero abitanti in ogni riga
    dfall = pd.merge(dfall, popolazione, on='Codice ISTAT')
    # sistema le colonne
    dfall.drop(['Abitanti_x', 'Rapporto', 'Provincia_x', 'ASL_x'], axis=1,
               inplace=True)
    dfall.rename({'Abitanti_y': 'Abitanti',
                  'ASL_y': 'ASL',
                  'Provincia_y': 'Provincia'},
                 axis=1, inplace=True)
    dfall = dfall.reindex(columns=COLONNE)
    print("Numero righe comuni con popolazione", dfall.shape[0])

    # calcola positivi 1000 abitanti
    dfall['Positivi 1000 abitanti'] = ((1000 * dfall['Positivi']) /
                                       dfall['Abitanti']).round(2)

    # aggiungi i dati di province e regione
    somme = aggrega_per_province(dfall, popolazione)
    dfall = pd.concat([dfall, somme], axis=0)
    print("Numero righe comuni, province, regione ", dfall.shape[0])

    # aggiungi i dati di ASL
    per_asl, tutte_asl = aggrega_per_asl(dfall, popolazione, asl)
    dfall = pd.concat([dfall, per_asl], axis=0)
    print("Numero righe comuni, province, regione, ASL ", dfall.shape[0])

    print("Numero comuni ", popolazione.shape[0])
    print("Numero province + regione ", len(PROV) + 1)
    print("Numero ASL", tutte_asl.shape[0])
    print("Numero giorni ", dfall['Data'].nunique())

    # ordina il dataset
    dfall.sort_values(by=['Tipo', 'Ente', 'Data'], inplace=True)

    # aggiungi in ogni riga la differenza in positivi su 1000 abitanti
    # rispetto al giorno Precedente
    dfall = aggiungi_delta_positivi(dfall, prima_data)

    # crea nome file output e scrivi il dataset
    last = dfall['Data'].max().replace("/", "_")
    # today = datetime.strftime(datetime.now(), "%Y_%m_%d")
    ofile = Path("data") / ("dati_per_tutto_il_periodo_" + last + ".csv")
    dfall.to_csv(ofile, index=False, sep=";")

    # creiamo un file separato per ogni "Tipo": PROV, REG, ASL, COM
    for tipo, descrizione in DESCRIZIONE_TIPO.items():
        dfiltrato = dfall[dfall['Tipo'] == tipo]
        ofile = Path("data") / ("dati_per_tutto_il_periodo_tipo_" + descrizione + ".csv")
        dfiltrato.to_csv(ofile, index=False, sep=";")


if __name__ == "__main__":
    main()
