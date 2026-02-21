"""
Web App per Diagnosi Energetiche
Streamlit application per la gestione completa delle diagnosi energetiche.

Avvio:
    streamlit run app_diagnosi.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
import io

# Configurazione pagina
st.set_page_config(
    page_title="Diagnosi Energetica",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Costanti
TEP_EE = 0.000187
TEP_GAS = 0.000836
TEP_GASOLIO = 0.00086
CO2_EE = 0.460  # kg/kWh
CO2_GAS = 1.950  # kg/Smc
CO2_GASOLIO = 2.650  # kg/litro

MESI = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# Inizializzazione session state con dati fittizi di esempio
if 'anagrafica' not in st.session_state:
    st.session_state.anagrafica = {
        'ragione_sociale': 'Industria Esempio S.r.l.',
        'piva': '01234567890',
        'indirizzo': 'Via Roma 42',
        'citta': 'Milano',
        'cap': '20100',
        'provincia': 'MI',
        'ateco': '25.11.00',
        'anno_rif': datetime.now().year - 1,
        'giorni_lav': 250,
        'turni': 1,
        'ore_turno': 8,
    }

if 'consumi_ee' not in st.session_state:
    st.session_state.consumi_ee = pd.DataFrame({
        'Mese': MESI,
        'kWh': [12500.0, 11800.0, 13200.0, 14500.0, 16000.0, 18500.0,
                19200.0, 17800.0, 15600.0, 14200.0, 13000.0, 12700.0],
        'Costo (€)': [4375.0, 4130.0, 4620.0, 5075.0, 5600.0, 6475.0,
                      6720.0, 6230.0, 5460.0, 4970.0, 4550.0, 4445.0],
    })

if 'consumi_gas' not in st.session_state:
    st.session_state.consumi_gas = pd.DataFrame({
        'Mese': MESI,
        'Smc': [3500.0, 3200.0, 2800.0, 1500.0, 800.0, 400.0,
                300.0, 300.0, 600.0, 1200.0, 2500.0, 3400.0],
        'Costo (€)': [3500.0, 3200.0, 2800.0, 1500.0, 800.0, 400.0,
                      300.0, 300.0, 600.0, 1200.0, 2500.0, 3400.0],
    })

if 'consumi_gasolio' not in st.session_state:
    st.session_state.consumi_gasolio = pd.DataFrame({
        'Mese': MESI,
        'Litri': [500.0, 450.0, 400.0, 200.0, 100.0, 50.0,
                  50.0, 50.0, 100.0, 250.0, 400.0, 500.0],
        'Costo (€)': [750.0, 675.0, 600.0, 300.0, 150.0, 75.0,
                      75.0, 75.0, 150.0, 375.0, 600.0, 750.0],
    })

if 'bilancio' not in st.session_state:
    st.session_state.bilancio = pd.DataFrame({
        'Categoria': ['ATTIVITA PRINCIPALI'] * 3 + ['SERVIZI AUSILIARI'] * 2 + ['SERVIZI GENERALI'] * 2,
        'Descrizione': ['Linea produzione 1', 'Linea produzione 2', 'Magazzino', 'Compressore', 'Pompe', 'Illuminazione', 'Climatizzazione'],
        'Potenza (kW)': [45.0, 30.0, 15.0, 22.0, 7.5, 12.0, 35.0],
        'Ore/giorno': [8.0, 8.0, 8.0, 8.0, 6.0, 10.0, 8.0],
        'Giorni/anno': [250, 250, 250, 250, 250, 300, 200],
        'Fattore carico': [0.70, 0.65, 0.40, 0.60, 0.50, 0.80, 0.55],
    })

if 'interventi' not in st.session_state:
    st.session_state.interventi = [
        {
            'nome': 'Sostituzione illuminazione con LED',
            'vettore': 'Energia Elettrica',
            'costo_inv': 15000.0,
            'costo_man': 200.0,
            'risparmio': 18000.0,
            'risparmio_euro': 6100.0,
            'vita_utile': 15,
            'tasso': 0.04,
            'payback': 2.5,
            'van': 52800.0,
            'note': 'Sostituzione corpi illuminanti con LED ad alta efficienza',
        },
        {
            'nome': 'Installazione inverter compressore',
            'vettore': 'Energia Elettrica',
            'costo_inv': 8000.0,
            'costo_man': 100.0,
            'risparmio': 8800.0,
            'risparmio_euro': 2980.0,
            'vita_utile': 10,
            'tasso': 0.04,
            'payback': 2.7,
            'van': 16160.0,
            'note': 'Inverter su compressore aria compressa da 22 kW',
        },
    ]

if 'fotovoltaico' not in st.session_state:
    st.session_state.fotovoltaico = {
        'potenza_kwp': 50.0,
        'anno_installazione': 2022,
        'produzione_annua': 57500.0,
        'autoconsumo_perc': 70,
    }


def calcola_totali():
    """Calcola i totali energetici."""
    ee_kwh = st.session_state.consumi_ee['kWh'].sum()
    ee_costo = st.session_state.consumi_ee['Costo (€)'].sum()
    gas_smc = st.session_state.consumi_gas['Smc'].sum()
    gas_costo = st.session_state.consumi_gas['Costo (€)'].sum()
    gasolio_l = st.session_state.consumi_gasolio['Litri'].sum()
    gasolio_costo = st.session_state.consumi_gasolio['Costo (€)'].sum()

    return {
        'ee_kwh': ee_kwh,
        'ee_tep': ee_kwh * TEP_EE,
        'ee_costo': ee_costo,
        'ee_co2': ee_kwh * CO2_EE / 1000,
        'gas_smc': gas_smc,
        'gas_tep': gas_smc * TEP_GAS,
        'gas_costo': gas_costo,
        'gas_co2': gas_smc * CO2_GAS / 1000,
        'gasolio_l': gasolio_l,
        'gasolio_tep': gasolio_l * TEP_GASOLIO,
        'gasolio_costo': gasolio_costo,
        'gasolio_co2': gasolio_l * CO2_GASOLIO / 1000,
        'tep_totale': ee_kwh * TEP_EE + gas_smc * TEP_GAS + gasolio_l * TEP_GASOLIO,
        'costo_totale': ee_costo + gas_costo + gasolio_costo,
        'co2_totale': ee_kwh * CO2_EE / 1000 + gas_smc * CO2_GAS / 1000 + gasolio_l * CO2_GASOLIO / 1000,
    }


def calcola_bilancio():
    """Calcola i consumi dal bilancio energetico."""
    df = st.session_state.bilancio.copy()
    df['kWh/anno'] = df['Potenza (kW)'] * df['Ore/giorno'] * df['Giorni/anno'] * df['Fattore carico']
    df['TEP'] = df['kWh/anno'] * TEP_EE
    return df


# Sidebar - Navigazione
st.sidebar.title("⚡ Diagnosi Energetica")

# Anno di riferimento sempre visibile
st.sidebar.selectbox(
    "📅 Anno di riferimento",
    options=list(range(2015, datetime.now().year + 1)),
    index=list(range(2015, datetime.now().year + 1)).index(st.session_state.anagrafica['anno_rif']),
    key="anno_sidebar",
    on_change=lambda: st.session_state.anagrafica.update({'anno_rif': st.session_state.anno_sidebar})
)

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Sezioni",
    ["🏠 Home", "🏢 Anagrafica", "📊 Consumi EE", "🔥 Consumi Gas",
     "⛽ Consumi Gasolio", "☀️ Fotovoltaico", "⚖️ Bilancio Energetico",
     "🔧 Interventi", "📈 Dashboard", "📄 Genera Report"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Riepilogo rapido")
totali = calcola_totali()
st.sidebar.metric("Energia totale", f"{totali['tep_totale']:.2f} TEP")
st.sidebar.metric("Spesa totale", f"€ {totali['costo_totale']:,.0f}")
st.sidebar.metric("CO2 totale", f"{totali['co2_totale']:.1f} ton")


# === PAGINE ===

if menu == "🏠 Home":
    st.title("⚡ Diagnosi Energetica")
    st.markdown("### Sistema di gestione diagnosi energetiche ai sensi del D.Lgs. 102/2014")

    st.markdown("""
    Benvenuto nel sistema di gestione delle diagnosi energetiche.
    Questa applicazione ti permette di:

    - 📝 **Inserire i dati anagrafici** dell'azienda
    - 📊 **Registrare i consumi** di energia elettrica, gas e gasolio
    - ☀️ **Gestire impianti fotovoltaici** e autoproduzione
    - ⚖️ **Creare il bilancio energetico** per area/reparto
    - 🔧 **Proporre interventi** di efficientamento con analisi economica
    - 📈 **Visualizzare dashboard** interattive
    - 📄 **Generare report** Excel e PDF professionali
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Anno di riferimento**\n\n{st.session_state.anagrafica['anno_rif']}")
    with col2:
        azienda = st.session_state.anagrafica['ragione_sociale'] or "Non definita"
        st.info(f"**Azienda**\n\n{azienda}")
    with col3:
        st.info(f"**Consumi totali**\n\n{totali['tep_totale']:.2f} TEP")

    st.markdown("---")
    st.markdown("### Come iniziare")
    st.markdown("""
    1. Vai in **Anagrafica** e inserisci i dati dell'azienda
    2. Inserisci i **Consumi** mensili (EE, Gas, Gasolio)
    3. Compila il **Bilancio Energetico** per area
    4. Aggiungi gli **Interventi** di efficientamento
    5. Controlla la **Dashboard** per una visione d'insieme
    6. **Genera il Report** finale
    """)


elif menu == "🏢 Anagrafica":
    st.title("🏢 Dati Anagrafici")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.anagrafica['ragione_sociale'] = st.text_input(
            "Ragione Sociale *",
            value=st.session_state.anagrafica['ragione_sociale']
        )
        st.session_state.anagrafica['piva'] = st.text_input(
            "Partita IVA *",
            value=st.session_state.anagrafica['piva']
        )
        st.session_state.anagrafica['indirizzo'] = st.text_input(
            "Indirizzo",
            value=st.session_state.anagrafica['indirizzo']
        )
        st.session_state.anagrafica['citta'] = st.text_input(
            "Città",
            value=st.session_state.anagrafica['citta']
        )

    with col2:
        st.session_state.anagrafica['cap'] = st.text_input(
            "CAP",
            value=st.session_state.anagrafica['cap']
        )
        st.session_state.anagrafica['provincia'] = st.text_input(
            "Provincia",
            value=st.session_state.anagrafica['provincia']
        )
        st.session_state.anagrafica['ateco'] = st.text_input(
            "Codice ATECO",
            value=st.session_state.anagrafica['ateco']
        )
        st.session_state.anagrafica['anno_rif'] = st.number_input(
            "Anno di riferimento *",
            min_value=2015,
            max_value=datetime.now().year,
            value=st.session_state.anagrafica['anno_rif']
        )

    st.markdown("### Regime operativo")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.anagrafica['giorni_lav'] = st.number_input(
            "Giorni lavorativi/anno",
            min_value=1, max_value=365,
            value=st.session_state.anagrafica['giorni_lav']
        )
    with col2:
        st.session_state.anagrafica['turni'] = st.number_input(
            "Numero turni",
            min_value=1, max_value=3,
            value=st.session_state.anagrafica['turni']
        )
    with col3:
        st.session_state.anagrafica['ore_turno'] = st.number_input(
            "Ore per turno",
            min_value=1, max_value=12,
            value=st.session_state.anagrafica['ore_turno']
        )

    if st.session_state.anagrafica['ragione_sociale']:
        st.success(f"✓ Anagrafica salvata per: {st.session_state.anagrafica['ragione_sociale']}")


elif menu == "📊 Consumi EE":
    st.title("📊 Consumi Energia Elettrica")

    st.markdown("Inserisci i consumi mensili di energia elettrica.")

    # Editor tabella
    edited_df = st.data_editor(
        st.session_state.consumi_ee,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Mese": st.column_config.TextColumn("Mese", disabled=True),
            "kWh": st.column_config.NumberColumn("kWh", min_value=0, format="%.0f"),
            "Costo (€)": st.column_config.NumberColumn("Costo (€)", min_value=0, format="%.2f"),
        }
    )
    st.session_state.consumi_ee = edited_df

    # Totali
    tot_kwh = edited_df['kWh'].sum()
    tot_costo = edited_df['Costo (€)'].sum()
    costo_medio = tot_costo / tot_kwh if tot_kwh > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Totale kWh", f"{tot_kwh:,.0f}")
    col2.metric("Totale €", f"{tot_costo:,.2f}")
    col3.metric("TEP", f"{tot_kwh * TEP_EE:.2f}")
    col4.metric("€/kWh medio", f"{costo_medio:.4f}")

    # Grafico
    if tot_kwh > 0:
        fig = px.bar(edited_df, x='Mese', y='kWh', title='Consumi mensili EE')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


elif menu == "🔥 Consumi Gas":
    st.title("🔥 Consumi Gas Naturale")

    st.markdown("Inserisci i consumi mensili di gas naturale.")

    edited_df = st.data_editor(
        st.session_state.consumi_gas,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Mese": st.column_config.TextColumn("Mese", disabled=True),
            "Smc": st.column_config.NumberColumn("Smc", min_value=0, format="%.0f"),
            "Costo (€)": st.column_config.NumberColumn("Costo (€)", min_value=0, format="%.2f"),
        }
    )
    st.session_state.consumi_gas = edited_df

    tot_smc = edited_df['Smc'].sum()
    tot_costo = edited_df['Costo (€)'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Totale Smc", f"{tot_smc:,.0f}")
    col2.metric("Totale €", f"{tot_costo:,.2f}")
    col3.metric("TEP", f"{tot_smc * TEP_GAS:.2f}")

    if tot_smc > 0:
        fig = px.bar(edited_df, x='Mese', y='Smc', title='Consumi mensili Gas')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


elif menu == "⛽ Consumi Gasolio":
    st.title("⛽ Consumi Gasolio")

    st.markdown("Inserisci i consumi mensili di gasolio.")

    edited_df = st.data_editor(
        st.session_state.consumi_gasolio,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Mese": st.column_config.TextColumn("Mese", disabled=True),
            "Litri": st.column_config.NumberColumn("Litri", min_value=0, format="%.0f"),
            "Costo (€)": st.column_config.NumberColumn("Costo (€)", min_value=0, format="%.2f"),
        }
    )
    st.session_state.consumi_gasolio = edited_df

    tot_litri = edited_df['Litri'].sum()
    tot_costo = edited_df['Costo (€)'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Totale Litri", f"{tot_litri:,.0f}")
    col2.metric("Totale €", f"{tot_costo:,.2f}")
    col3.metric("TEP", f"{tot_litri * TEP_GASOLIO:.2f}")


elif menu == "☀️ Fotovoltaico":
    st.title("☀️ Impianto Fotovoltaico")

    st.markdown("Inserisci i dati dell'impianto fotovoltaico (se presente).")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.fotovoltaico['potenza_kwp'] = st.number_input(
            "Potenza installata (kWp)",
            min_value=0.0, max_value=10000.0, step=0.1,
            value=st.session_state.fotovoltaico['potenza_kwp']
        )
        st.session_state.fotovoltaico['anno_installazione'] = st.number_input(
            "Anno installazione",
            min_value=2000, max_value=datetime.now().year,
            value=st.session_state.fotovoltaico['anno_installazione'] or datetime.now().year
        )

    with col2:
        st.session_state.fotovoltaico['produzione_annua'] = st.number_input(
            "Produzione annua (kWh)",
            min_value=0.0, step=100.0,
            value=st.session_state.fotovoltaico['produzione_annua']
        )
        st.session_state.fotovoltaico['autoconsumo_perc'] = st.slider(
            "Percentuale autoconsumo (%)",
            min_value=0, max_value=100,
            value=st.session_state.fotovoltaico['autoconsumo_perc']
        )

    # Stima produzione se non inserita
    if st.session_state.fotovoltaico['potenza_kwp'] > 0 and st.session_state.fotovoltaico['produzione_annua'] == 0:
        stima = st.session_state.fotovoltaico['potenza_kwp'] * 1150  # Nord Italia
        st.info(f"💡 Produzione stimata (Nord Italia): {stima:,.0f} kWh/anno")
        if st.button("Usa stima"):
            st.session_state.fotovoltaico['produzione_annua'] = stima
            st.rerun()

    if st.session_state.fotovoltaico['produzione_annua'] > 0:
        autoconsumo = st.session_state.fotovoltaico['produzione_annua'] * st.session_state.fotovoltaico['autoconsumo_perc'] / 100
        immissione = st.session_state.fotovoltaico['produzione_annua'] - autoconsumo

        col1, col2, col3 = st.columns(3)
        col1.metric("Produzione", f"{st.session_state.fotovoltaico['produzione_annua']:,.0f} kWh")
        col2.metric("Autoconsumo", f"{autoconsumo:,.0f} kWh")
        col3.metric("Immissione rete", f"{immissione:,.0f} kWh")


elif menu == "⚖️ Bilancio Energetico":
    st.title("⚖️ Bilancio Energetico")

    st.markdown("Definisci la ripartizione dei consumi elettrici per area/reparto.")

    # Editor
    edited_df = st.data_editor(
        st.session_state.bilancio,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Categoria": st.column_config.SelectboxColumn(
                "Categoria",
                options=["ATTIVITA PRINCIPALI", "SERVIZI AUSILIARI", "SERVIZI GENERALI", "ALTRO"]
            ),
            "Descrizione": st.column_config.TextColumn("Descrizione"),
            "Potenza (kW)": st.column_config.NumberColumn("Potenza (kW)", min_value=0, format="%.2f"),
            "Ore/giorno": st.column_config.NumberColumn("Ore/giorno", min_value=0, max_value=24, format="%.1f"),
            "Giorni/anno": st.column_config.NumberColumn("Giorni/anno", min_value=0, max_value=365),
            "Fattore carico": st.column_config.NumberColumn("Fattore carico", min_value=0, max_value=1, format="%.2f"),
        }
    )
    st.session_state.bilancio = edited_df

    # Calcoli
    df_calc = calcola_bilancio()

    st.markdown("### Risultati")

    # Riepilogo per categoria
    riepilogo = df_calc.groupby('Categoria').agg({'kWh/anno': 'sum', 'TEP': 'sum'}).reset_index()
    totale_kwh = df_calc['kWh/anno'].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(riepilogo, use_container_width=True)
        st.metric("Totale bilancio", f"{totale_kwh:,.0f} kWh")

    with col2:
        if totale_kwh > 0:
            fig = px.pie(riepilogo, values='kWh/anno', names='Categoria', title='Ripartizione consumi')
            st.plotly_chart(fig, use_container_width=True)

    # Confronto con consumi reali
    consumi_reali = st.session_state.consumi_ee['kWh'].sum()
    if consumi_reali > 0 and totale_kwh > 0:
        diff = totale_kwh - consumi_reali
        diff_perc = diff / consumi_reali * 100

        st.markdown("### Confronto con consumi reali")
        col1, col2, col3 = st.columns(3)
        col1.metric("Bilancio stimato", f"{totale_kwh:,.0f} kWh")
        col2.metric("Consumi da bollette", f"{consumi_reali:,.0f} kWh")
        col3.metric("Differenza", f"{diff:+,.0f} kWh ({diff_perc:+.1f}%)")

        if abs(diff_perc) > 20:
            st.warning("⚠️ La differenza supera il 20%. Verifica i dati del bilancio o considera l'autoconsumo fotovoltaico.")


elif menu == "🔧 Interventi":
    st.title("🔧 Interventi di Efficientamento")

    st.markdown("Aggiungi le proposte di intervento di efficientamento energetico.")

    # Form nuovo intervento
    with st.expander("➕ Aggiungi nuovo intervento", expanded=len(st.session_state.interventi) == 0):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome intervento")
            vettore = st.selectbox("Vettore risparmiato", ["Energia Elettrica", "Gas Naturale", "Gasolio"])
            costo_inv = st.number_input("Costo investimento (€)", min_value=0.0, step=100.0)
            costo_man = st.number_input("Costo manutenzione annuo (€)", min_value=0.0, step=10.0)

        with col2:
            risparmio = st.number_input("Risparmio energetico annuo (kWh/Smc/l)", min_value=0.0, step=100.0)
            vita_utile = st.number_input("Vita utile (anni)", min_value=1, max_value=30, value=10)
            tasso = st.number_input("Tasso attualizzazione (%)", min_value=0.0, max_value=20.0, value=4.0) / 100

            # Costo medio vettore
            if vettore == "Energia Elettrica":
                tot_kwh = st.session_state.consumi_ee['kWh'].sum()
                tot_costo = st.session_state.consumi_ee['Costo (€)'].sum()
                costo_medio = tot_costo / tot_kwh if tot_kwh > 0 else 0.36
            elif vettore == "Gas Naturale":
                tot = st.session_state.consumi_gas['Smc'].sum()
                tot_costo = st.session_state.consumi_gas['Costo (€)'].sum()
                costo_medio = tot_costo / tot if tot > 0 else 1.0
            else:
                tot = st.session_state.consumi_gasolio['Litri'].sum()
                tot_costo = st.session_state.consumi_gasolio['Costo (€)'].sum()
                costo_medio = tot_costo / tot if tot > 0 else 1.5

            st.info(f"Costo medio {vettore}: € {costo_medio:.4f}")

        note = st.text_area("Note")

        if st.button("Aggiungi intervento"):
            if nome and costo_inv > 0 and risparmio > 0:
                # Calcolo payback e VAN
                risparmio_euro = risparmio * costo_medio - costo_man
                payback = costo_inv / risparmio_euro if risparmio_euro > 0 else 999

                # VAN
                van = -costo_inv
                for anno in range(1, vita_utile + 1):
                    van += risparmio_euro / ((1 + tasso) ** anno)

                intervento = {
                    'nome': nome,
                    'vettore': vettore,
                    'costo_inv': costo_inv,
                    'costo_man': costo_man,
                    'risparmio': risparmio,
                    'risparmio_euro': risparmio_euro,
                    'vita_utile': vita_utile,
                    'tasso': tasso,
                    'payback': payback,
                    'van': van,
                    'note': note,
                }
                st.session_state.interventi.append(intervento)
                st.success(f"✓ Intervento '{nome}' aggiunto!")
                st.rerun()
            else:
                st.error("Compila tutti i campi obbligatori (nome, costo, risparmio)")

    # Lista interventi
    if st.session_state.interventi:
        st.markdown("### Interventi proposti")

        for i, interv in enumerate(st.session_state.interventi):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 0.5])
                col1.write(f"**{interv['nome']}**")
                col2.write(f"€ {interv['costo_inv']:,.0f}")
                col3.write(f"€ {interv['risparmio_euro']:,.0f}/anno")
                col4.write(f"PB: {interv['payback']:.1f}a")

                van_color = "green" if interv['van'] > 0 else "red"
                col4.markdown(f"VAN: <span style='color:{van_color}'>€ {interv['van']:,.0f}</span>", unsafe_allow_html=True)

                if col5.button("🗑️", key=f"del_{i}"):
                    st.session_state.interventi.pop(i)
                    st.rerun()

        # Riepilogo
        st.markdown("---")
        tot_inv = sum(i['costo_inv'] for i in st.session_state.interventi)
        tot_risp = sum(i['risparmio_euro'] for i in st.session_state.interventi)
        tot_van = sum(i['van'] for i in st.session_state.interventi)

        col1, col2, col3 = st.columns(3)
        col1.metric("Investimento totale", f"€ {tot_inv:,.0f}")
        col2.metric("Risparmio totale", f"€ {tot_risp:,.0f}/anno")
        col3.metric("VAN totale", f"€ {tot_van:,.0f}")


elif menu == "📈 Dashboard":
    st.title("📈 Dashboard Energetica")

    totali = calcola_totali()

    # KPI principali
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Energia Totale", f"{totali['tep_totale']:.2f} TEP")
    col2.metric("Spesa Totale", f"€ {totali['costo_totale']:,.0f}")
    col3.metric("Emissioni CO2", f"{totali['co2_totale']:.1f} ton")
    if totali['ee_kwh'] > 0:
        col4.metric("Costo medio EE", f"€ {totali['ee_costo']/totali['ee_kwh']:.4f}/kWh")

    st.markdown("---")

    # Grafici
    col1, col2 = st.columns(2)

    with col1:
        # Ripartizione per vettore (TEP)
        data_tep = pd.DataFrame({
            'Vettore': ['Energia Elettrica', 'Gas Naturale', 'Gasolio'],
            'TEP': [totali['ee_tep'], totali['gas_tep'], totali['gasolio_tep']]
        })
        data_tep = data_tep[data_tep['TEP'] > 0]

        if not data_tep.empty:
            fig = px.pie(data_tep, values='TEP', names='Vettore', title='Ripartizione consumi (TEP)')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Ripartizione costi
        data_costo = pd.DataFrame({
            'Vettore': ['Energia Elettrica', 'Gas Naturale', 'Gasolio'],
            'Costo': [totali['ee_costo'], totali['gas_costo'], totali['gasolio_costo']]
        })
        data_costo = data_costo[data_costo['Costo'] > 0]

        if not data_costo.empty:
            fig = px.pie(data_costo, values='Costo', names='Vettore', title='Ripartizione spesa (€)')
            st.plotly_chart(fig, use_container_width=True)

    # Andamento mensile
    st.markdown("### Andamento mensile consumi")

    df_mensile = pd.DataFrame({
        'Mese': MESI,
        'Energia Elettrica (kWh)': st.session_state.consumi_ee['kWh'],
        'Gas Naturale (Smc)': st.session_state.consumi_gas['Smc'],
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(name='EE (kWh)', x=df_mensile['Mese'], y=df_mensile['Energia Elettrica (kWh)']))
    fig.add_trace(go.Bar(name='Gas (Smc)', x=df_mensile['Mese'], y=df_mensile['Gas Naturale (Smc)']))
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Bilancio energetico
    df_bil = calcola_bilancio()
    if df_bil['kWh/anno'].sum() > 0:
        st.markdown("### Bilancio energetico per categoria")
        riepilogo = df_bil.groupby('Categoria')['kWh/anno'].sum().reset_index()
        fig = px.bar(riepilogo, x='Categoria', y='kWh/anno', title='Consumi per categoria')
        st.plotly_chart(fig, use_container_width=True)


elif menu == "📄 Genera Report":
    st.title("📄 Genera Report")

    st.markdown("Genera i file di output della diagnosi energetica.")

    # Verifica dati minimi
    totali = calcola_totali()
    has_anagrafica = bool(st.session_state.anagrafica['ragione_sociale'])
    has_consumi = totali['tep_totale'] > 0

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Checklist")
        st.checkbox("Anagrafica compilata", value=has_anagrafica, disabled=True)
        st.checkbox("Consumi inseriti", value=has_consumi, disabled=True)
        st.checkbox("Bilancio energetico", value=calcola_bilancio()['kWh/anno'].sum() > 0, disabled=True)
        st.checkbox("Interventi proposti", value=len(st.session_state.interventi) > 0, disabled=True)

    with col2:
        st.markdown("### Riepilogo")
        st.write(f"**Azienda:** {st.session_state.anagrafica['ragione_sociale'] or 'N/D'}")
        st.write(f"**Anno:** {st.session_state.anagrafica['anno_rif']}")
        st.write(f"**Energia totale:** {totali['tep_totale']:.2f} TEP")
        st.write(f"**Spesa totale:** € {totali['costo_totale']:,.0f}")
        st.write(f"**Interventi:** {len(st.session_state.interventi)}")

    st.markdown("---")

    if has_anagrafica and has_consumi:
        nome_azienda = st.session_state.anagrafica['ragione_sociale'].replace(' ', '_').replace('.', '')

        col1, col2 = st.columns(2)

        # --- GENERA EXCEL ---
        with col1:
            if st.button("📊 Genera Excel", use_container_width=True):
                from openpyxl import Workbook
                from openpyxl.styles import Font

                wb = Workbook()

                # Foglio SINTESI
                ws = wb.active
                ws.title = "SINTESI"
                ws['A1'] = f"DIAGNOSI ENERGETICA - {st.session_state.anagrafica['ragione_sociale']}"
                ws['A1'].font = Font(bold=True, size=14)
                ws['A2'] = f"Anno di riferimento: {st.session_state.anagrafica['anno_rif']}"

                ws['A4'] = "Vettore"
                ws['B4'] = "Consumo"
                ws['C4'] = "Unità"
                ws['D4'] = "TEP"
                ws['E4'] = "Costo (€)"

                ws['A5'] = "Energia Elettrica"
                ws['B5'] = totali['ee_kwh']
                ws['C5'] = "kWh"
                ws['D5'] = totali['ee_tep']
                ws['E5'] = totali['ee_costo']

                ws['A6'] = "Gas Naturale"
                ws['B6'] = totali['gas_smc']
                ws['C6'] = "Smc"
                ws['D6'] = totali['gas_tep']
                ws['E6'] = totali['gas_costo']

                ws['A7'] = "Gasolio"
                ws['B7'] = totali['gasolio_l']
                ws['C7'] = "litri"
                ws['D7'] = totali['gasolio_tep']
                ws['E7'] = totali['gasolio_costo']

                ws['A8'] = "TOTALE"
                ws['D8'] = totali['tep_totale']
                ws['E8'] = totali['costo_totale']

                # Foglio CONSUMI_EE
                ws_ee = wb.create_sheet("CONSUMI_EE")
                ws_ee['A1'] = "Mese"
                ws_ee['B1'] = "kWh"
                ws_ee['C1'] = "Costo (€)"
                for i, row in st.session_state.consumi_ee.iterrows():
                    ws_ee[f'A{i+2}'] = row['Mese']
                    ws_ee[f'B{i+2}'] = row['kWh']
                    ws_ee[f'C{i+2}'] = row['Costo (€)']

                # Foglio BILANCIO
                ws_bil = wb.create_sheet("BILANCIO")
                df_bil = calcola_bilancio()
                ws_bil['A1'] = "Categoria"
                ws_bil['B1'] = "Descrizione"
                ws_bil['C1'] = "kWh/anno"
                ws_bil['D1'] = "TEP"
                for i, row in df_bil.iterrows():
                    ws_bil[f'A{i+2}'] = row['Categoria']
                    ws_bil[f'B{i+2}'] = row['Descrizione']
                    ws_bil[f'C{i+2}'] = row['kWh/anno']
                    ws_bil[f'D{i+2}'] = row['TEP']

                # Foglio INTERVENTI
                if st.session_state.interventi:
                    ws_int = wb.create_sheet("INTERVENTI")
                    ws_int['A1'] = "Intervento"
                    ws_int['B1'] = "Investimento (€)"
                    ws_int['C1'] = "Risparmio (€/anno)"
                    ws_int['D1'] = "Payback (anni)"
                    ws_int['E1'] = "VAN (€)"
                    for i, interv in enumerate(st.session_state.interventi):
                        ws_int[f'A{i+2}'] = interv['nome']
                        ws_int[f'B{i+2}'] = interv['costo_inv']
                        ws_int[f'C{i+2}'] = interv['risparmio_euro']
                        ws_int[f'D{i+2}'] = interv['payback']
                        ws_int[f'E{i+2}'] = interv['van']

                # Salva in memoria (BytesIO)
                buffer_excel = io.BytesIO()
                wb.save(buffer_excel)
                buffer_excel.seek(0)

                st.session_state.excel_data = buffer_excel.getvalue()
                st.session_state.excel_filename = f"DIAGNOSI_{nome_azienda}_{st.session_state.anagrafica['anno_rif']}.xlsx"
                st.success("✓ File Excel generato!")

        # --- GENERA PDF ---
        with col2:
            if st.button("📄 Genera PDF", use_container_width=True):
                try:
                    from reportlab.lib import colors
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib.units import cm
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
                    from reportlab.lib.enums import TA_CENTER

                    buffer_pdf = io.BytesIO()

                    doc = SimpleDocTemplate(buffer_pdf, pagesize=A4,
                                          rightMargin=2*cm, leftMargin=2*cm,
                                          topMargin=2*cm, bottomMargin=2*cm)

                    styles = getSampleStyleSheet()
                    styles.add(ParagraphStyle(name='TitoloReport', parent=styles['Title'],
                                            fontSize=20, textColor=colors.HexColor('#1a5276'),
                                            alignment=TA_CENTER))

                    story = []

                    # Copertina
                    story.append(Spacer(1, 3*cm))
                    story.append(Paragraph("DIAGNOSI ENERGETICA", styles['TitoloReport']))
                    story.append(Paragraph("ai sensi del D.Lgs. 102/2014", styles['Heading2']))
                    story.append(Spacer(1, 2*cm))
                    story.append(Paragraph(f"<b>{st.session_state.anagrafica['ragione_sociale']}</b>", styles['TitoloReport']))
                    story.append(Paragraph(f"{st.session_state.anagrafica['indirizzo']}", styles['Normal']))
                    story.append(Paragraph(f"{st.session_state.anagrafica['cap']} {st.session_state.anagrafica['citta']} ({st.session_state.anagrafica['provincia']})", styles['Normal']))
                    story.append(Spacer(1, 2*cm))
                    story.append(Paragraph(f"Anno di riferimento: {st.session_state.anagrafica['anno_rif']}", styles['Heading2']))
                    story.append(PageBreak())

                    # Sintesi
                    story.append(Paragraph("QUADRO DI SINTESI ENERGETICA", styles['Heading1']))

                    data = [
                        ['Vettore', 'Consumo', 'TEP', 'Costo (€)'],
                        ['Energia Elettrica', f"{totali['ee_kwh']:,.0f} kWh", f"{totali['ee_tep']:.2f}", f"{totali['ee_costo']:,.0f}"],
                        ['Gas Naturale', f"{totali['gas_smc']:,.0f} Smc", f"{totali['gas_tep']:.2f}", f"{totali['gas_costo']:,.0f}"],
                        ['Gasolio', f"{totali['gasolio_l']:,.0f} litri", f"{totali['gasolio_tep']:.2f}", f"{totali['gasolio_costo']:,.0f}"],
                        ['TOTALE', '', f"{totali['tep_totale']:.2f}", f"{totali['costo_totale']:,.0f}"],
                    ]

                    t = Table(data, colWidths=[5*cm, 4*cm, 3*cm, 3*cm])
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d5e8d4')),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 1*cm))

                    # Emissioni
                    story.append(Paragraph("EMISSIONI CO2", styles['Heading2']))
                    story.append(Paragraph(f"Emissioni totali: {totali['co2_totale']:.2f} tonnellate/anno", styles['Normal']))

                    # Interventi
                    if st.session_state.interventi:
                        story.append(PageBreak())
                        story.append(Paragraph("INTERVENTI DI EFFICIENTAMENTO", styles['Heading1']))

                        data_int = [['Intervento', 'Investimento', 'Risparmio/anno', 'Payback', 'VAN']]
                        for interv in st.session_state.interventi:
                            data_int.append([
                                interv['nome'][:30],
                                f"€ {interv['costo_inv']:,.0f}",
                                f"€ {interv['risparmio_euro']:,.0f}",
                                f"{interv['payback']:.1f} anni",
                                f"€ {interv['van']:,.0f}"
                            ])

                        t = Table(data_int, colWidths=[5*cm, 2.5*cm, 2.5*cm, 2*cm, 2.5*cm])
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ]))
                        story.append(t)

                    doc.build(story)
                    buffer_pdf.seek(0)

                    st.session_state.pdf_data = buffer_pdf.getvalue()
                    st.session_state.pdf_filename = f"REPORT_DE_{nome_azienda}_{st.session_state.anagrafica['anno_rif']}.pdf"
                    st.success("✓ File PDF generato!")

                except Exception as e:
                    st.error(f"Errore nella generazione del PDF: {e}")

        # Download buttons persistenti (fuori dal st.button)
        st.markdown("---")
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            if 'excel_data' in st.session_state:
                st.download_button(
                    label="⬇️ Scarica Excel",
                    data=st.session_state.excel_data,
                    file_name=st.session_state.excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        with col_dl2:
            if 'pdf_data' in st.session_state:
                st.download_button(
                    label="⬇️ Scarica PDF",
                    data=st.session_state.pdf_data,
                    file_name=st.session_state.pdf_filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
    else:
        st.warning("⚠️ Compila almeno l'anagrafica e inserisci i consumi prima di generare il report.")

    # Salva/Carica progetto
    st.markdown("---")
    st.markdown("### Salva/Carica progetto")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salva progetto"):
            progetto = {
                'anagrafica': st.session_state.anagrafica,
                'consumi_ee': st.session_state.consumi_ee.to_dict(),
                'consumi_gas': st.session_state.consumi_gas.to_dict(),
                'consumi_gasolio': st.session_state.consumi_gasolio.to_dict(),
                'bilancio': st.session_state.bilancio.to_dict(),
                'interventi': st.session_state.interventi,
                'fotovoltaico': st.session_state.fotovoltaico,
            }

            nome_azienda = st.session_state.anagrafica['ragione_sociale'].replace(' ', '_').replace('.', '') or "progetto"

            st.session_state.json_data = json.dumps(progetto, indent=2).encode('utf-8')
            st.session_state.json_filename = f"progetto_{nome_azienda}.json"
            st.success("✓ Progetto salvato!")

        if 'json_data' in st.session_state:
            st.download_button(
                label="⬇️ Scarica progetto",
                data=st.session_state.json_data,
                file_name=st.session_state.json_filename,
                mime="application/json"
            )

    with col2:
        uploaded_file = st.file_uploader("Carica progetto (.json)", type="json")
        if uploaded_file is not None:
            progetto = json.load(uploaded_file)

            st.session_state.anagrafica = progetto['anagrafica']
            st.session_state.consumi_ee = pd.DataFrame(progetto['consumi_ee'])
            st.session_state.consumi_gas = pd.DataFrame(progetto['consumi_gas'])
            st.session_state.consumi_gasolio = pd.DataFrame(progetto['consumi_gasolio'])
            st.session_state.bilancio = pd.DataFrame(progetto['bilancio'])
            st.session_state.interventi = progetto['interventi']
            st.session_state.fotovoltaico = progetto['fotovoltaico']

            st.success("✓ Progetto caricato!")
            st.rerun()


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Diagnosi Energetica v1.0*")
st.sidebar.markdown("*D.Lgs. 102/2014 - UNI CEI EN 16247*")
