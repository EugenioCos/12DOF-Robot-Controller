const { app, BrowserWindow } = require('electron')
const path = require("path");

const createWindow = () => {
  const win = new BrowserWindow({
    width: 1280,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, "events.js"),
      contextIsolation: true,
      nodeIntegration: true,
    },
  });

  win.loadFile('index.html');
  // Open the DevTools.
  win.setFullScreen(true);
  win.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow()
})
