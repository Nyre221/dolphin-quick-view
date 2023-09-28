# Requisiti:

Per vedere l'anterprima dei file doc,docx,xls,xlsx,ods,odp,ppt,pptx e odt è necessario avere libreoffice installato.  
Se stati usando la versione flatpak è necessario dare a libreoffice l'accesso alla cartella `/tmp/`.

Per fare questo è sufficente (dopo aver installato libreoffice) digitare il comando: `sudo flatpak override org.libreoffice.LibreOffice --filesystem=/tmp` , oppure scaricando `flatseal`e dare i permessi da lì.

Libreoffice: https://flathub.org/apps/org.libreoffice.LibreOffice  
Flatseal: https://flathub.org/apps/com.github.tchx84.Flatseal

# Errori:

## Error: source file could not be loaded.

Questo può accadere se stai usando la versione di libreoffice installata tramite gestore dei pacchetti e non hai installato tutti i componenti.
Per esempio, su ubuntu è necessario installare `libreoffice-writer` (docx,doc,odt), `libreoffice-calc` (xlsx,xls,csv,ods) e `libreoffice-impress` (odp,ppt,pptx).  
Se stai usando la versione flatpak, assicurati di non aver installato anche la versione del gestore dei pacchetti.

## Errore: Libreoffice non è installato.

Devi installare libreoffice per vedere l'anteprima.

## Errore: Il documento ha impiegato troppo tempo a caricare.

Viene mostrato se il file ha troppe pagine e impiega troppo tempo a caricare.

## Errore: File non trovato: Flatpak potrebbe non essere configurato correttamente.

Questo accade quando la versione flatpak di libreoffice non ha accesso alla cartella `/tmp`.

Puoi risolvere con il comando `sudo flatpak override org.libreoffice.LibreOffice --filesystem=/tmp` o usando `flatseal`.

Procedura con Flatseal:


![Screenshot-28-09-2023-CEST](https://github.com/Nyre221/dolphin-quick-view/assets/104171042/42fd30cf-4ca3-4afd-a63b-147c214217fa)






