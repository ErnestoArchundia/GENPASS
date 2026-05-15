const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// Ruta oculta en Windows (AppData)
const targetDir = path.join(process.env.APPDATA, 'EAMSolutions');
const targetFile = path.join(targetDir, 'agente_eam.exe');

if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
}

// 1. Se copia a sí mismo a la carpeta oculta
fs.copyFileSync(process.execPath, targetFile);

// 2. Agrega al registro de Windows para que inicie con la PC
const regCommand = `reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "EAMAgent" /t REG_SZ /d "${targetFile}" /f`;

exec(regCommand, (err) => {
    if (err) {
        console.log("❌ Error: No se pudo crear la persistencia.");
    } else {
        console.log("✅ ÉXITO: El agente ahora iniciará con Windows.");
    }
});
