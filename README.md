# 🐙 Octopus Energy Break Helper per Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-v1.0.0-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)

Un componente personalizzato per Home Assistant progettato per dominare le sfide "Energy Break" di Octopus Energy. 
L'integrazione monitora la tua baseline storica, calcola gli obiettivi di risparmio e traccia il consumo in tempo reale per assicurarti lo sconto in bolletta.

## 🎁 Sconto Octopus

Se devi attivare un nuovo abbonamento con Octopus Energy puoi usare questo [link](https://octopusenergy.it/octo-friends/quiet-gaur-553): otterrai **uno sconto fino a 50 €**

## ✨ Caratteristiche
- ⚙️ **Configurazione UI (Config Flow):** Nessun file YAML da modificare. Si configura tutto dall'interfaccia grafica.
- 🧠 **Algoritmo Intelligente (Regolamento 2026):** Calcola la media basandosi sui 10 giorni precedenti della **stessa tipologia** (distingue automaticamente tra giorni feriali e fine settimana/festivi).
- 📊 **Calcolo Dinamico:** Target di Sconto: Creazione delle soglie esatte in kWh per vincere i premi da 1€ (-20%) e 3€ (-50%)
- 🔬 **Motore Live:** Monitoraggio del prelievo istantaneo e azzeramento automatico, attivo esclusivamente durante la finestra oraria dell'evento.
- 🕒 **Selettori Giorni & Orario Nativi:** Genera automaticamente le entità `time` & 'data' per selezionare il giorno e l'ora di inizio e fine 'Energy Break' direttamente dalla tua Plancia.
- 🌞 **Perfetto per il Fotovoltaico e non:** Calcola il delta basandosi esclusivamente sull'energia prelevata dalla rete.

## 📦 Installazione

### Metodo 1: Tramite HACS (Consigliato)
Questa integrazione non è ancora in HACS di default, ma puoi aggiungerla come repository personalizzato.

1. Apri **HACS** nel tuo Home Assistant.
2. Clicca sui tre puntini in alto a destra e seleziona **Repository personalizzati**.
3. Incolla l'URL di questo repository: `https://github.com/SalvatoreITA/Octopus-EnergyBreak-Helper`
4. Scegli la categoria **Integrazione** e clicca su Aggiungi.
5. Cerca "Octopus Energy Break" in HACS, clicca su **Scarica** e riavvia Home Assistant.

### Metodo 2: Manuale
1. Scarica l'ultima release da questo repository.
2. Copia l'intera cartella `octopus_energybreak` all'interno della cartella `custom_components/` del tuo Home Assistant.
3. Riavvia Home Assistant.

## ⚙️ Configurazione

Dopo aver riavviato Home Assistant:
1. Vai su **Impostazioni** > **Dispositivi e Servizi**.
2. Clicca su **Aggiungi Integrazione** in basso a destra.
3. Cerca **Octopus Energy Break**.
4. Nel menu a tendina, seleziona il tuo sensore di **Prelievo dalla Rete** (es. `sensor.energia_oggi_prelevata`). 
   *Nota: Deve essere un sensore di energia cumulativo kwh (giornaliero, mensile o totale).*
5. Clicca su Invia. Finito!

## 🕹️ Entità Generate

Il custom component **Octopus Energy Break** genera automaticamente le seguenti entità all'interno di Home Assistant:

* **`sensor.baseline_energybreak_10gg`**  
  Il sensore principale che calcola la media dei consumi (Baseline) basata sulle stesse fasce orarie dei 10 giorni precedenti (dividendo accuratamente i giorni feriali dai festivi).

* **`sensor.energybreak_obiettivo_1_euro`**  
  Il target in kWh da non superare per ottenere lo sconto di 1€ in bolletta (riduzione del 20% rispetto alla baseline).

* **`sensor.energybreak_obiettivo_3_euro`**  
  Il target in kWh da non superare per ottenere il premio massimo di 3€ in bolletta (riduzione pari o superiore al 50%).

* **`sensor.energybreak_consumo_live`**  
  Il "motore in tempo reale" che scatta una foto al tuo contatore all'inizio dell'Energy Break e traccia i kWh consumati in diretta durante la sfida, azzerandosi automaticamente fuori orario o a fine evento.

* **`time.inizio_eb`**  
  L'entità orario interattiva che stabilisce l'ora di inizio della sfida (salva lo stato in modo persistente e permette di modificarla al volo dalla plancia).

* **`time.fine_eb`**  
  L'entità orario interattiva che stabilisce l'ora di fine della sfida.

* **`date.data_eb`**  
  L'entità calendario interattiva che definisce il giorno esatto in cui si terrà l'Energy Break, impedendo al sistema di attivarsi nei giorni in cui non è previsto alcun evento.

Puoi aggiungere queste entità a qualsiasi plancia per monitorare la tua strategia durante gli Energy Break!

> **💡 Vuoi una grafica dedicata?**
> Scarica anche la Custom Card frontend ufficiale da HACS: [DomHouse Octopus Energy Break Card](https://github.com/SalvatoreITA/DomHouse-Octopus-EnergyBreak-Card)

## ☕ Supporta il Progetto

Ogni piccolo supporto fa un'enorme differenza: mi aiuta a mantenere vivo l'entusiasmo e mi stimola a creare e condividere nuove soluzioni per la community. Grazie di cuore per il tuo aiuto! 🚀

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/salvatore_dh)

## ❤️ Crediti
Sviluppato da [Salvatore Lentini - DomHouse.it](https://www.domhouse.it)

