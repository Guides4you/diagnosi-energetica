# Diagnosi Energetica - Web App

Applicazione web per la gestione delle diagnosi energetiche ai sensi del D.Lgs. 102/2014.

## Funzionalità

- Gestione anagrafica azienda
- Inserimento consumi energetici (EE, Gas, Gasolio)
- Gestione impianti fotovoltaici
- Bilancio energetico per area/reparto
- Proposte di intervento con calcolo Payback e VAN
- Dashboard interattiva con grafici
- Generazione report Excel e PDF
- Salvataggio/caricamento progetti

## Installazione locale

### Requisiti
- Python 3.9 o superiore

### Passi

```bash
# 1. Clona o scarica il repository
git clone https://github.com/TUO_USERNAME/diagnosi-energetica.git
cd diagnosi-energetica

# 2. Crea ambiente virtuale (opzionale ma consigliato)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Avvia l'app
streamlit run app_diagnosi.py
```

L'app sarà disponibile su http://localhost:8501

## Deploy Online

### Streamlit Community Cloud (Gratuito)

1. Carica il progetto su GitHub
2. Vai su https://share.streamlit.io
3. Clicca "New app"
4. Seleziona il repository e il file `app_diagnosi.py`
5. Clicca "Deploy"

L'app sarà online in pochi minuti con URL tipo: `https://tuo-nome-app.streamlit.app`

## Struttura file

```
├── app_diagnosi.py          # Applicazione principale
├── requirements.txt         # Dipendenze Python
├── elabora_diagnosi.py      # Script elaborazione Excel
├── genera_report_pdf.py     # Generatore PDF standalone
├── crea_template.py         # Generatore template Excel
└── README_APP.md            # Questo file
```

## Licenza

Uso interno - Tutti i diritti riservati.
