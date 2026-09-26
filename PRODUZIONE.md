# Cose Mancanti Per Andare In Produzione

Questo documento raccoglie i punti da chiudere prima di usare Vortex con dati reali o utenti esterni.

La release pubblica mantiene Qdrant nella rete privata Compose e pubblica l'API
soltanto su loopback. Admin e reader condividono un unico archivio: tutti gli
utenti autenticati possono leggere tutti i progetti. L'isolamento per cliente
o per progetto richiede ulteriori controlli applicativi.

## Bloccanti Prima Del Primo Deploy

- [ ] Configurare HTTPS dietro reverse proxy o load balancer.
- [x] Rimuovere Tailwind via CDN e generare un bundle CSS locale.
- [x] Richiedere autenticazione per download e preview e verificare i percorsi di storage.
- [ ] Introdurre permessi per progetto prima di usare l'app per archivi con accessi differenziati.
- [ ] Definire backup e restore per SQLite, upload, preview e Qdrant.
- [ ] Aggiungere log strutturati per login, upload, indicizzazione, ricerca, errori e cancellazioni.
- [ ] Aggiungere un sistema di monitoraggio per salute API, spazio disco, Qdrant e job di indicizzazione.

## Backend E Dati

- [ ] Decidere se SQLite e' sufficiente per il carico previsto o se migrare a PostgreSQL.
- [ ] Introdurre migrazioni database versionate invece di modifiche implicite all'avvio.
- [ ] Spostare l'indicizzazione lunga su worker/job queue dedicata, non solo background task del processo web.
- [ ] Rendere idempotente e riprendibile l'indicizzazione dopo crash o restart.
- [ ] Aggiungere cleanup per upload o preview rimasti orfani.
- [ ] Aggiungere policy di retention o archiviazione dei progetti eliminati.
- [ ] Precaricare o cacheare i modelli FastEmbed in fase di deploy, evitando download al primo utilizzo.
- [ ] Versionare i modelli usati e documentare come reindicizzare quando cambiano.
- [ ] Configurare Qdrant con persistenza, backup e risorse dedicate.
- [ ] Verificare concorrenza su SQLite, upload simultanei e ricerche durante indicizzazione.
- [ ] Aggiungere limiti di timeout per estrazione testo, rendering PDF e embedding.

## Sicurezza E Accessi

- [ ] Definire ruoli e permessi reali oltre a `admin` e `user`, se servono.
- [ ] Aggiungere cambio password per l'utente corrente.
- [ ] Aggiungere reset password amministrativo tracciato.
- [ ] Aggiungere audit log per operazioni sensibili: login, creazione utenti, cambio ruolo, delete progetto.
- [ ] Valutare 2FA o SSO se il sistema verra' esposto fuori rete interna.
- [ ] Aggiungere protezione CSRF se le API restano cookie-based.
- [ ] Definire CORS esplicitamente, anche se oggi UI e API sono same-origin.
- [ ] Sanitizzare e normalizzare nomi file, titoli e descrizioni in tutti i punti di rendering.

## Frontend E UX

- [x] Costruire CSS statico locale ed eliminare lo script CDN.
- [ ] Aggiungere stati di caricamento coerenti per upload, indicizzazione e ricerca.
- [ ] Mostrare progresso o stato dettagliato per file in indicizzazione.
- [ ] Gestire meglio errori utente: file non supportato, PDF troppo grande, modello non disponibile.

## Qualita Ricerca

- [ ] Creare un dataset di valutazione realistico con almeno 100-200 query raccolte da utenti aziendali.
- [ ] Definire soglie minime prima della prod: Top-1 >= 85%, Top-3 >= 95%, zero regressioni su query critiche.
- [ ] Separare metriche per ricerca titolo/codice, testo documentale, visuale, metadata e query miste.
- [ ] Aggiungere test automatico in CI/CD che fallisce se la suite di valutazione ricerca scende sotto le soglie.
- [ ] Salvare in modo anonimo query reali, click sui risultati, no-result e risultato aperto per migliorare ranking.
- [ ] Aggiungere sinonimi/tassonomia per dominio reale: immobili, retail, interni, impianti, materiali, codici commessa.
- [ ] Estrarre metadata strutturati dai documenti: tipologia, mq, piano, prezzo, camere, cliente, anno, materiali, stato.
- [ ] Migliorare OCR/estrazione PDF per tavole tecniche: alcune pagine generano testo numerico rumoroso.
- [ ] Valutare Docling, PaddleOCR o pipeline OCR dedicata per schede scansionate e PDF tecnici complessi.
- [ ] Versionare la tassonomia visuale usata per caption/tag e prevedere reindex quando cambia.
- [ ] Aggiungere feedback utente "risultato utile/non utile" per tuning del ranking.
- [ ] Monitorare query lente, query senza risultati e query con bassa confidenza.
- [ ] Documentare procedura periodica di reindex dopo cambio modelli, OCR o tassonomia visuale.

## Deploy E Operativita

- [ ] Definire target di deploy: VPS, Docker Compose, Kubernetes, NAS o macchina locale.
- [ ] Configurare reverse proxy con HTTPS, compressione e limiti upload coerenti.
- [ ] Definire piano di aggiornamento senza perdere dati o interrompere indicizzazioni.
- [ ] Documentare procedura di backup, restore e reindicizzazione.

## Test Minimi Da Aggiungere

- [x] Test API per autenticazione, logout e permessi admin/user.
- [x] Test API per creazione e delete progetto.
- [ ] Test API per modifica progetto e gestione utenti.
- [x] Test upload di testo, PDF non valido e formato non supportato.
- [ ] Test ricerca con indice vuoto, indice popolato e Qdrant non disponibile.
- [ ] Test migrazione o inizializzazione database.
- [ ] Test UI almeno sui flussi principali con Playwright.
- [ ] Test Docker build e avvio completo con Qdrant.
- [x] Test di regressione sulla mancata esposizione di Qdrant e sul binding locale della demo.

I test API usano storage SQLite/Qdrant reale e sostituiscono solo gli embedding
con vettori deterministici. Non misurano la qualità semantica dei risultati.
