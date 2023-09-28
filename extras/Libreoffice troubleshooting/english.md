# Requirements:

To preview doc, docx, xls, xlsx, ods, odp, ppt, pptx and odt files you need to have libreoffice installed.
If you are using the flatpak version you need to give libreoffice access to the `/tmp/` folder.  
To do this, simply (after installing libreoffice) type the command: `sudo flatpak override org.libreoffice.LibreOffice --filesystem=/tmp` , or use `flatseal` and give permissions from there.

Libreoffice: https://flathub.org/apps/org.libreoffice.LibreOffice  
Flatseal: https://flathub.org/apps/com.github.tchx84.Flatseal


# Errors:

## Error: source file could not be loaded.

This can happen if you are using the version of libreoffice installed via package manager and you have not installed all components.  
For example, on ubuntu you need to install `libreoffice-writer` (docx,doc,odt), `libreoffice-calc` (xlsx,xls,csv,ods) and `libreoffice-impress` (odp,ppt,pptx).  
If you are using the flatpak version, make sure you don't also have the package manager version installed.

## Error: Libreoffice is not installed.

You need to install libreoffice to see the preview.

## Error: The document took too long to load.

This is shown if the file has too many pages and is taking too long to load.

## Error: File not found: Flatpak may not be configured correctly.

This happens when the flatpak version of libreoffice does not have access to the `/tmp` folder.

You can fix it with the command `sudo flatpak override org.libreoffice.LibreOffice --filesystem=/tmp` or by using `flatseal`.

Procedure with Flatseal:

![Screenshot-28-09-2023-CEST-1](https://github.com/Nyre221/dolphin-quick-view/assets/104171042/186f45d4-751a-49c9-bc8c-f8827fcfc688)
