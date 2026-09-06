const { app, BrowserWindow, shell } = require("electron");
const path = require("path");

// URL of the running Next.js app. In dev, run `npm run dev` inside /frontend
// (localhost:3000) BEFORE launching Electron. For a packaged build, point
// this at your deployed URL or serve the Next.js `out`/`build` output locally.
const APP_URL = process.env.APP_URL || "http://localhost:3000";

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 680,
    backgroundColor: "#080C14",
    title: "Crypto AI Assistant",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadURL(APP_URL);

  // Open external links (e.g. news sources) in the OS browser, not inside the app
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
