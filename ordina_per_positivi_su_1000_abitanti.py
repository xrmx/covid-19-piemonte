"""
il programma legge un file csv scaricato dal sito della Regione Piemonte

con il numero di positivi al Coronavirus per ogni comune della regione e crea
i file in output
data/comuni_piemonte_ordinati_per_densita_contagio.csv
data/comuni_piemonte_ordinati_per_densita_contagio.xls

con i comuni piemontesi ordinati in ordine decrescente per numero di positivi
per mille abitanti
"""
import argparse
import pandas as pd
from pathlib import Path

PROV = {"001": "TO", "002": "VC", "003": "NO", "004": "CN", "005": "AT",
        "006": "AL", "096": "BI", "103": "VCO"}


def provincia(row):
    return PROV[str(row["Codice ISTAT"][:3])]


def main():
    parser = argparse.ArgumentParser(description='Ordina comuni piemontesi' +
                                     ' per positivi per 1000 abitanti')

    parser.add_argument('positivi_per_comune')
    args = parser.parse_args()

    # crea il dataframe a partire dal file in input
    casi = pd.read_csv(args.positivi_per_comune, sep=";",
                       dtype={"Codice ISTAT": "str"})
    fname = Path(args.positivi_per_comune).stem
    fdata = fname.replace("dati_", "") \
                 .replace("_da_regione_piemonte", "")
    # carica dati_2020_04_09_da_regione_piemonte.csv che ha l'informazione
    # relativa al numero di abitanti per ogni comune
    ifile = Path("data") / "dati_2020_04_09_da_regione_piemonte.csv"
    df = pd.read_csv(ifile, sep=";",
                     dtype={"Codice ISTAT": "str"})
    popolazione = df[['Abitanti', 'Codice ISTAT']] \
        .drop_duplicates(keep='first')
    # aggiungi la colonna 'Abitanti' al dataset
    casi = pd.merge(popolazione, casi, on="Codice ISTAT") \
        .drop('Abitanti_y', axis=1) \
        .rename({'Abitanti_x': 'Abitanti'}, axis=1)

    # calcola il numero di positivi per 1000 abitanti
    casi['Rapporto'] = (1000 * casi['Positivi']) / casi['Abitanti']
    casi['Rapporto'] = casi['Rapporto'].round(0).astype(int)

    # aggiungi la provincia
    casi['Provincia'] = casi.apply(provincia, axis=1)

    # crea dataset ordinato decrescente per numero positivi per 1000 abitanti
    casis = casi.sort_values(by='Rapporto', ascending=False) \
                .reset_index(drop=True)

    # prepara il dataset
    casis = casis.rename({'Rapporto': 'Positivi per 100 abitanti'}, axis=1)
    casis['Verificato'] = ""
    colonne = ['Comune', 'Provincia', 'Positivi', 'Positivi per 100 abitanti',
               'Abitanti', 'Verificato', 'Data', 'Codice ISTAT']
    casis = casis.reindex(columns=colonne)

    # definizione del nome dei file di output
    ofile = Path("data") / \
                ("comuni_ordinati_per_densita_contagio_" + fdata + '.csv')

    # scrivi il dataset su file in formato csv
    casis.to_csv(ofile, index=False, sep=";", columns=colonne)


if __name__ == "__main__":
    main()
