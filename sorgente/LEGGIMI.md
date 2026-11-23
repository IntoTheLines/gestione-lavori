# Sorgente di Gestione Lavori

- `../index.html` e file vicini: app per telefono (GitHub Pages, installabile).
- `../programma/`: ultima versione del programma PC + `versione.json` (da qui il programma si aggiorna da solo).
- `Lavori-browser.html`: versione da aprire nel browser sul PC.
- `programma-pc/`: programma Windows (Tauri v2). `ui/index.html` = interfaccia.
- `supabase/1-crea-tabelle.sql`: tabelle dell'archivio online (il codice del team NON è qui).
- `patch/`: script usati per aggiungere le funzioni (telefono, appunti).

## Compilare il programma PC (da Linux)
```
apt-get install gcc-mingw-w64-x86-64 nsis
rustup target add x86_64-pc-windows-gnu
cd programma-pc && cargo build --release --target x86_64-pc-windows-gnu
cp target/x86_64-pc-windows-gnu/release/gestione-lavori.exe portatile/gl.exe
cp target/x86_64-pc-windows-gnu/release/WebView2Loader.dll portatile/
cd portatile && makensis portatile.nsi   # crea "Gestione Lavori.exe" (un solo file)
```
Nuova versione: alzare il numero in `Cargo.toml`, `tauri.conf.json` e `!define VER` in `portatile.nsi`,
poi copiare exe e `versione.json` in `../programma/`.

Ogni modifica all'interfaccia va fatta in 3 file: `../index.html`, `programma-pc/ui/index.html`, `Lavori-browser.html`.
