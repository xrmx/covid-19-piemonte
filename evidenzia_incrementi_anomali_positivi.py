"""
questo programma esamina i file con i dati relativi ai positivi al COVID 19
resi disponibili dalla Regione Piemonte e evidenzia i casi in cui vi sia un
incremento di positivi rispetto al giorno precedente superiore a una certa
percentuale
"""
import argparse
import csv
from datetime import datetime
# import glob
from pathlib import Path
import pandas as pd

PROV = {"001": "TO", "002": "VC", "003": "NO", "004": "CN", "005": "AT",
        "006": "AL", "096": "BI", "103": "VCO"}


def provincia(row):
    return PROV[str(row["Codice ISTAT"][:3])]


def main():
    parser = argparse.ArgumentParser(description='Evidenzia casi di anomalo' +
                                                 ' incremento di positivi' +
                                                 ' in un comune')
    parser.add_argument('-p', '--percentuale', default=40,
                        help="incremento percentuale oltre cui c'è anomalia")
    parser.add_argument('-n', '--numero_giorni', default=10,
                        help='numero giorni da non considerare dal 25 marzo')

    args = parser.parse_args()
    first = args.numero_giorni

    delta = (100 + args.percentuale) / 100
    # opzione da definire per evitare noiosi messaggi di errore
    pd.set_option('mode.chained_assignment', None)

    # elenco dei file csv con i dati dei positivi
    # ifiles = sorted(glob.glob("data/dati*.csv"))
    ifiles = sorted(Path('data').glob("dati*.csv"))
    # il primo file ha anche le informazione sul numero abitanti per comune
    print(ifiles[0])
    df = pd.read_csv(ifiles[0], sep=";",
                     dtype={"Codice ISTAT": "string"})
    popolazione = df[['Abitanti', 'Codice ISTAT']] \
        .drop_duplicates(keep='first')

    # carica i file con i dati
    for ifile in ifiles[1:]:
        print(ifile)
        df1 = pd.read_csv(ifile, sep=";",
                          dtype={"Codice ISTAT": "string"})
        df = pd.concat([df, df1], axis=0)
        del df1

    # aggiungi la provincia
    df['Provincia'] = df.apply(provincia, axis=1)

    # ottieni la lista dei comuni (codici ISTAT)
    comuni = list(df['Codice ISTAT'].unique())

    # crea csv writer
    today = datetime.strftime(datetime.now(), "%Y_%m_%d")
    ofile = Path("data") / ("incrementi_positivi_anomali_" + today + ".csv")

    with open(ofile, 'wt') as fout:
        writer = csv.writer(fout, delimiter=";")
        row = ['Comune', 'Provincia', 'Data', 'Positivi giorno precedente',
               'Positivi']
        writer.writerow(row)
        # loop sui comuni evidenziando aumento di positivi
        # > del parametro -p di input
        for comune in comuni:
            dfc = df[df['Codice ISTAT'] == comune].sort_values(by='Data')
            abitanti = int(popolazione[popolazione['Codice ISTAT'] == comune]
                                      ['Abitanti'])
            dfc['Abitanti'] = abitanti
            dfc['Rapporto'] = (1000 * dfc['Positivi']) / dfc['Abitanti']
            positivi = list(dfc['Positivi'])
            prev = positivi[first - 1]
            # sono ignorati i casi con meno di 5 positivi per 1000 abitanti
            for idx, item in enumerate(positivi[first:]):
                if item > 5 and item > delta * prev:
                    rowdf = dfc.iloc[idx + first, :]
                    row = [rowdf['Comune'], rowdf['Provincia'], rowdf['Data'],
                           prev, rowdf['Positivi']]
                    writer.writerow(row)
                prev = item


if __name__ == "__main__":
    main()
