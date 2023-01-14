const { app, BrowserWindow } = require('electron');
const axios = require('axios');
const url = 'http://localhost:5000';

let mainWindow;
let gameId;

app.on('ready', () => {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });

    mainWindow.loadURL(`file://${__dirname}/index.html`);

    mainWindow.webContents.on('did-finish-load', () => {
        createNewGame();
    });
});

function createNewGame() {
    axios.post(`${url}/new_game`)
        .then(response => {
            gameId = response.data.game_id;
            mainWindow.webContents.send('game-id', gameId);
        })
        .catch(error => {
            console.log(error);
        });
}

function playRound() {
    axios.post(`${url}/play`, {
        game_id: gameId,
        player_id: 'player1'
    })
        .then(response => {
            getGameState();
        })
        .catch(error => {
            console.log(error);
        });
}

function getGameState() {
    axios.get(`${url}/game_state?game_id=${gameId}`)
        .then(response => {
            const state = response.data.state;
            mainWindow.webContents.send('game-state', state);
        })
        .catch(error => {
            console.log(error);
        });
}
