# La mia soluzione al problema posto

Buongiorno e grazie per il tempo dedicato alla lettura di questa soluzione. Nella storia dei commit, potete trovare la mia versione dopo due ore, la prima versione funzionante per risolvere il task al 100% e questa versione, contenente alcuni aggiustamenti e miglioramenti generici.
## Pacchetti e librerie
Per risolvere il problema, ho utilizzato alcune librerie che dovreste trovate già installate in python 3:
- argparse
- json
- logging
- xml.etree.ElementTree
- logging
- warnings
Ho utilizzato un ambiente conda con versione python 3.9.11, con unico pacchetto "esterno" da installare Pillow (trovabile in requirements.txt per un'installazione veloce)
Lato stile, ho fatto affidamento sul formatter black e sul linter pycodestyle.

## Approccio
Ho creato un unico file app.py contenente la parte di risoluzione logica e alcune funzioni di supporto.
Vengono letti i parametri di input e vengono parsati, uno alla volta, i file XML estraendo di volta in volta le informazioni utili. Per ogni XML, l'immagine corrispondente viene elaborata ed eventualmente modificata, aggiornando così in contemporanea le informazioni utili. Queste informazioni sono raccolte in liste di oggetti, le cui classi custom sono definite in un file dedicato.
Ho scelto questo approccio ad oggetti per abitudine e gusti personali e perchè nelle fasi iniziali non mi era ancora chiarissimo quanto ogni classe fosse effettivamente unica (necessitando magari di metodi dedicati)
NB: per il resize delle immagini ho applicato un approccio "original_ratio", per cercare di mantenere le proporzioni originali.

## Run
Per lanciare il programma basta posizionarsi nella cartella di progetto ed eseguire "python app.py cartella1 cartella2 cartella3"
NB: a seconda della versione, potrebbe essere richiesto di usare "python3" anzi che "python"
NB: l'ordine delle cartelle è immagini, xml, immagini_output

## Risultati
Dopo l'esecuzione troveremo il file output.json nel formato richiesto e le immagini modificate (o non) nella cartella indicata come output.
Eventuali errori comuni (cartelle, file, ecc) dovrebbero essere gestite a livello di codice tramite blocchi try/except e con informazioni fornite dal logger.

## Miglioramenti?
- Migliore gestione eccezione
- Logger più informativo
- Migliore incapsulamento codice (moduli dedicati per funzioni di utilità)
- Valutare miglioramento performance nel non usare gli oggetti, ma creando liste di dizionari già in fase di parsing XML
- Migliore gestione numeri decimali (magari in base a richieste di cliente/utilizzatore)
- Aggiungere alcuni check intermedi nel caso alcuni campi del file XML non dovessero essere trovati.
