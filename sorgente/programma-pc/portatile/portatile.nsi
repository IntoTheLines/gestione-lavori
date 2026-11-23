; Programma portatile: un solo file. All'avvio estrae il programma in
; %LOCALAPPDATA%\Gestione Lavori\app e lo apre, senza installare niente.
Unicode true
Name "Gestione Lavori"
OutFile "Gestione Lavori.exe"
Icon "icon.ico"
RequestExecutionLevel user
SilentInstall silent
SetCompressor /SOLID lzma
VIProductVersion "1.4.0.0"
VIAddVersionKey "ProductName" "Gestione Lavori"
VIAddVersionKey "FileDescription" "Gestione Lavori"
VIAddVersionKey "FileVersion" "1.4.0"
VIAddVersionKey "CompanyName" "Jacopo"
VIAddVersionKey "LegalCopyright" "Jacopo"
Section
  !define VER "1.4.0"
  SetOutPath "$LOCALAPPDATA\Gestione Lavori\app-${VER}"
  SetOverwrite try
  File "WebView2Loader.dll"
  File /oname=GestioneLavori.exe "gl.exe"
  Exec '"$LOCALAPPDATA\Gestione Lavori\app-${VER}\GestioneLavori.exe" --dir "$EXEDIR" --exe "$EXEPATH"'
SectionEnd
