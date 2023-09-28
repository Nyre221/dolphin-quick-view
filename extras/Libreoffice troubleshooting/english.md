# Requirements:

To preview doc, docx, xls, xlsx, ods, odp, ppt, pptx and odt files you need to have libreoffice installed.
If you are using the flatpak version you need to give libreoffice access to the `/tmp/` folder.

To do this, simply (after installing libreoffice) type the command: `sudo flatpak override org.libreoffice.LibreOffice --filesystem=/tmp` , or by downloading `flatseal` and giving permissions from there.

# Errors:

## Error: source file could not be loaded.


This can happen if you are using the version of libreoffice installed via package manager and you have not installed all components.  
For example, on ubuntu you need to install `libreoffice-writer` (docx,doc,odt), `libreoffice-calc` (xlsx,xls,csv,ods) and `libreoffice-impress` (odp,ppt,pptx).  
If you are using the flatpak version, make sure you don't also have the package manager version installed.

## Error: Libreoffice is not installed.

You need to install libreoffice to see the preview.

## Error: File not found: Flatpak may not be configured correctly.

This happens when the flatpak version of libreoffice does not have access to the `/tmp` folder.

You can fix it with the command `sudo flatpak override org.libreoffice.LibreOffice --filesystem=/tmp` or by using `flatseal`.
