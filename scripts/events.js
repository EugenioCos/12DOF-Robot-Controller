const { exec, spawn } = require("child_process");
const nodeConsole = require("console");
const { connect } = require("net");
const { text } = require("stream/consumers");

let port = "81";
let ip = "192.168.1.190";

const terminalConsole = new nodeConsole.Console(process.stdout, process.stderr);
let sliders;
let connect_button;
let legs;
let tibias;
let child;

function print(data) {
    terminalConsole.log(data);
    console.log(data);
}

function noChild() {
    if (child && !child.killed) {
        return false;
    } else {
        alert("Avvio richiesto !");
        return true;
    }
}

function send(text) {
    if(noChild()) return;
    print(`Sending ${text}`);
    child.stdin.write(text+"\n\r");
}

// ------------------- MESSAGES ELABORATION ---------------------------------

function handleResponse(data) {
    print(`[JS] received data: ${data}`);
    words = data.toString().replace(/[\n\r\t]/gm, "").split(' ').reverse();
    EvalResponse(words);
}

function EvalResponse(words) {
    while(words.length > 0){
        cmd = words.pop();
        if(cmd == "Connesso") {
            alert("Connesso al rover!");
            changeConnectButton();
        } else if(cmd == "Angoli:"){
            let angoli = [0,0,0,0,0,0,0,0,0,0,0,0];
            for(let i = 0; i < 12; i++) {
                angoli[i] = parseInt(words.pop());
            }
            updateLegs([angoli[1], angoli[7], angoli[4], angoli[10]]);
            updateTibias([angoli[2], angoli[8], angoli[5], angoli[11]]);
            updateSliders(angoli)
        }
    }
}

function updateLegs(angles) {
    legs.forEach((leg, index) => {
        leg.style.transform = `rotate(${-angles[index]}deg)`;
    });
}

function updateTibias(angles) {
    tibias.forEach((tibia, index) => {
        tibia.style.transform = `rotate(${-angles[index]}deg)`;
    });
}

function updateSliders(angles) {
    sliders.forEach((slider) => {
        if(slider.getAttribute('cmd') != "setang") return;
        let i = parseInt(slider.getAttribute('ang'));
        if((i + 1) % 3 != 0) limit = parseInt(slider.getAttribute('max'));
        else limit = parseInt(slider.getAttribute('min'));
        if(Math.abs(angles[i]) - Math.abs(limit) > 0) return;
        let input = slider.shadowRoot.querySelector('input');
        input.value = angles[i];

        let fraction = angles[i] / limit;
        if(fraction > 1) return;
        if((i + 1) % 3 == 0) fraction = 1 - fraction;
        let container = slider.shadowRoot.querySelector('.container');
        container.style.setProperty('--_end-fraction', fraction);
        //print(container);
    });
}

// ------------------- BUTTONS ---------------------------------

function startPython() {
    print("Initializing main.py");
    child = spawn("python3", ["-i", "python/main.py"]);
    print(`PID: ${child.pid}`);
    child.stdout.on("data", (data) => handleResponse(data));
}

function connectRover() {
    if(noChild()) return;
    let state = connect_button.innerHTML;
    if(state == "Connetti") send("connect "+ip+" "+port);
    else send("disconnetti");
}

function changeConnectButton(){
    let state = connect_button.innerHTML;
    if(state == "Connetti") connect_button.innerHTML = "Disconnetti";
    else connect_button.innerHTML = "Connetti";
}

function sendRover(){
    text = textInput();
    send(text);
}

function stopPython() {
    if(noChild()) return;
    print("Stopping program");
    child.kill(3);
}

function textInput() {
    target = document.getElementById('text_input');
    const internalInput = target.shadowRoot.querySelector('.input');
    return internalInput.value;
}

function updateIpPort() {
    value = textInput();
    const regex = new RegExp(/\b\d{3}\.\d{3}\.\d{1,3}\.\d{1,3} \d{1,5}\b/);
    if(regex.test(value)){
        words = value.split(' ');
        ip = words[0];
        port = words[1];
    }
}

function walkRover() {
    if(noChild()) return;
    send("walk");
}

function stopRover() {
    if(noChild()) return;
    send("stop");
}

function resetRover() {
    if(noChild()) return;
    send("reset");
}

function syncRover() {
    if(noChild()) return;
    send("sync");
}

document.addEventListener("DOMContentLoaded", () => {
    print("DOMContentLoaded");
    document
        .getElementById("start_button")
        .addEventListener("click", startPython);
    connect_button = document.getElementById("connect_button");
    connect_button.addEventListener("click", connectRover);
    document
        .getElementById("send_button")
        .addEventListener("click", sendRover);
    document
        .getElementById("terminate_button")
        .addEventListener("click", stopPython);
    document
        .getElementById("walk_button")
        .addEventListener("click", walkRover);
    document
        .getElementById("stop_button")
        .addEventListener("click", stopRover);
    document
        .getElementById("reset_button")
        .addEventListener("click", resetRover);
    document
        .getElementById("sync_button")
        .addEventListener("click", syncRover);
    document
        .getElementById("text_input")
        .addEventListener("change", updateIpPort);
    
    sliders = document.querySelectorAll('md-slider');
    sliders.forEach((slider) => {
        slider.addEventListener('input', (event) => {
            target = event.currentTarget;
            let cmd = target.getAttribute('cmd');
            let ang = target.getAttribute('ang');
            input = target.shadowRoot.querySelector('input');
            let value = input.ariaValueText;
            send(`${cmd} ${ang} ${value}`);
        });
    });

    legs = document.querySelectorAll(".leg");
    tibias = document.querySelectorAll(".tibia");
});
