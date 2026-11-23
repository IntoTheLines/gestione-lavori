#![windows_subsystem = "windows"]
use std::{fs, path::PathBuf, time::UNIX_EPOCH};
use tauri::Manager;

fn cfg_path(app: &tauri::AppHandle) -> PathBuf {
    let d = app.path().app_config_dir().unwrap_or_else(|_| PathBuf::from("."));
    let _ = fs::create_dir_all(&d);
    d.join("impostazioni.json")
}
fn read_cfg(app: &tauri::AppHandle) -> serde_json::Value {
    fs::read_to_string(cfg_path(app)).ok().and_then(|s| serde_json::from_str(&s).ok()).unwrap_or(serde_json::json!({}))
}
fn mtime(p: &str) -> Result<f64, String> {
    let m = fs::metadata(p).map_err(|e| e.to_string())?.modified().map_err(|e| e.to_string())?;
    Ok(m.duration_since(UNIX_EPOCH).map(|d| d.as_millis() as f64).unwrap_or(0.0))
}
fn start_dir(app: &tauri::AppHandle) -> PathBuf {
    if let Some(p) = read_cfg(app)["archivio"].as_str() {
        if let Some(d) = PathBuf::from(p).parent() { if d.exists() { return d.to_path_buf(); } }
    }
    for k in ["OneDrive", "OneDriveConsumer", "USERPROFILE"] {
        if let Ok(v) = std::env::var(k) { if PathBuf::from(&v).exists() { return PathBuf::from(v); } }
    }
    PathBuf::from(".")
}

#[tauri::command]
fn get_saved(app: tauri::AppHandle) -> Option<String> {
    let saved = read_cfg(&app)["archivio"].as_str().map(String::from);
    if let Some(p) = &saved { if PathBuf::from(p).exists() { return saved; } }
    // cerca l'archivio vicino al programma: cartella del programma e cartella sopra (Calendario)
    // --dir <cartella>: cartella dove si trova il programma portatile (passata dal lanciatore)
    let args: Vec<String> = std::env::args().collect();
    let start = args.iter().position(|a| a == "--dir").and_then(|i| args.get(i + 1)).map(PathBuf::from)
        .or_else(|| std::env::current_exe().ok().and_then(|e| e.parent().map(|x| x.to_path_buf())));
    if let Some(sd) = start {
        let mut d = Some(sd);
        for _ in 0..2 {
            if let Some(dir) = d.clone() {
                let f = dir.join("archivio-lavori.json");
                if f.exists() {
                    let s = f.to_string_lossy().to_string();
                    let _ = set_saved(app.clone(), s.clone());
                    return Some(s);
                }
                d = dir.parent().map(|x| x.to_path_buf());
            }
        }
    }
    // nessun archivio trovato: ne crea uno nuovo in Documenti\Gestione Lavori
    let base = app.path().document_dir().unwrap_or_else(|_| PathBuf::from("."));
    let dir = base.join("Gestione Lavori");
    let f = dir.join("archivio-lavori.json");
    if !f.exists() {
        let _ = fs::create_dir_all(&dir);
        let _ = fs::write(&f, "{\n  \"eliminati\": {},\n  \"clienti\": [],\n  \"lavori\": [],\n  \"utenti\": []\n}");
    }
    if f.exists() {
        let s = f.to_string_lossy().to_string();
        let _ = set_saved(app.clone(), s.clone());
        return Some(s);
    }
    saved
}
#[tauri::command]
fn set_saved(app: tauri::AppHandle, p: String) -> Result<(), String> {
    let mut c = read_cfg(&app); c["archivio"] = serde_json::json!(p);
    fs::write(cfg_path(&app), serde_json::to_string_pretty(&c).unwrap()).map_err(|e| e.to_string())
}
#[tauri::command]
async fn pick(app: tauri::AppHandle, mode: String) -> Option<String> {
    let d = rfd::FileDialog::new().add_filter("Archivio lavori", &["json"]).set_directory(start_dir(&app));
    let r = match mode.as_str() {
        "open" => d.set_title("Scegli il file archivio-lavori.json").pick_file(),
        "backup" => d.set_title("Salva backup").set_file_name(&format!("backup-lavori.json")).save_file(),
        _ => d.set_title("Dove creare l'archivio").set_file_name("archivio-lavori.json").save_file(),
    };
    r.map(|p| p.to_string_lossy().to_string())
}
#[tauri::command]
fn read(p: String) -> Result<serde_json::Value, String> {
    let t = fs::read_to_string(&p).map_err(|e| e.to_string())?;
    Ok(serde_json::json!({ "text": t, "mtime": mtime(&p)? }))
}
#[tauri::command]
fn write(p: String, t: String) -> Result<f64, String> {
    if let Some(d) = PathBuf::from(&p).parent() { let _ = fs::create_dir_all(d); }
    fs::write(&p, t).map_err(|e| e.to_string())?;
    mtime(&p)
}
#[tauri::command]
fn show(p: String) {
    #[cfg(windows)]
    { let _ = std::process::Command::new("explorer").arg(format!("/select,{}", p)).spawn(); }
    #[cfg(not(windows))]
    { let _ = p; }
}


fn arg(name: &str) -> Option<String> {
    let a: Vec<String> = std::env::args().collect();
    a.iter().position(|x| x == name).and_then(|i| a.get(i + 1)).cloned()
}
#[tauri::command]
fn app_info(app: tauri::AppHandle) -> serde_json::Value {
    // toglie le copie estratte delle versioni vecchie
    if let Ok(me) = std::env::current_exe() {
        if let (Some(cur), Some(base)) = (me.parent(), me.parent().and_then(|p| p.parent())) {
            if base.file_name().map(|n| n == "Gestione Lavori").unwrap_or(false) { if let Ok(rd) = fs::read_dir(base) {
                for e in rd.flatten() {
                    let p = e.path();
                    let n = e.file_name().to_string_lossy().to_string();
                    if p != cur && p.is_dir() && (n == "app" || n.starts_with("app-")) { let _ = fs::remove_dir_all(&p); }
                }
            } }
        }
    }
    serde_json::json!({ "versione": app.package_info().version.to_string(), "exe": arg("--exe") })
}
// sostituisce il programma portatile con la versione nuova e lo riavvia
#[tauri::command]
fn update_self(app: tauri::AppHandle, b64: String) -> Result<(), String> {
    use base64::Engine;
    let exe = arg("--exe").ok_or("percorso del programma sconosciuto")?;
    let data = base64::engine::general_purpose::STANDARD.decode(b64.as_bytes()).map_err(|e| e.to_string())?;
    if data.len() < 200_000 || &data[0..2] != b"MZ" { return Err("file scaricato non valido".into()); }
    let p = PathBuf::from(&exe);
    let newp = p.with_extension("exe.nuovo");
    let oldp = p.with_extension("exe.vecchio");
    fs::write(&newp, &data).map_err(|e| e.to_string())?;
    let _ = fs::remove_file(&oldp);
    fs::rename(&p, &oldp).map_err(|e| e.to_string())?;
    if let Err(e) = fs::rename(&newp, &p) { let _ = fs::rename(&oldp, &p); return Err(e.to_string()); }
    let _ = fs::remove_file(&oldp);
    std::process::Command::new(&p).spawn().map_err(|e| e.to_string())?;
    app.exit(0);
    Ok(())
}
// copia datata dell'archivio, una al giorno, tiene le ultime 30
#[tauri::command]
fn daily_backup(p: String, giorno: String) -> Result<(), String> {
    let src = PathBuf::from(&p);
    let dir = src.parent().ok_or("cartella")?.join("backup");
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let dst = dir.join(format!("archivio-{}.json", giorno));
    if dst.exists() { return Ok(()); }
    fs::copy(&src, &dst).map_err(|e| e.to_string())?;
    let mut v: Vec<PathBuf> = fs::read_dir(&dir).map_err(|e| e.to_string())?.filter_map(|e| e.ok().map(|e| e.path()))
        .filter(|x| x.file_name().map(|n| { let n = n.to_string_lossy(); n.starts_with("archivio-") && n.ends_with(".json") }).unwrap_or(false)).collect();
    v.sort();
    while v.len() > 30 { let _ = fs::remove_file(v.remove(0)); }
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_saved, set_saved, pick, read, write, show, app_info, update_self, daily_backup])
        .run(tauri::generate_context!())
        .expect("errore avvio");
}

