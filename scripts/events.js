const { exec, spawn } = require("child_process");
const nodeConsole = require("console");
const { connect } = require("net");

const terminalConsole = new nodeConsole.Console(process.stdout, process.stderr);
let sliders;
let legs;
let tibias;
let child;

function noChild() {
    if (child && !child.killed) {
        return false;
    } else {
        alert("Avvio richiesto !");
        return true;
    }
}

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
        let container = slider.shadowRoot.querySelector('.container');
        let fraction = angles[i] / limit;
        if(fraction > 1) return;
        if((i + 1) % 3 == 0) fraction = 1 - fraction;
        container.style.setProperty('--_end-fraction', fraction);
        //print(container);
    });
}

function print(data) {
    terminalConsole.log(data);
    console.log(data);
}

function startPython() {
    print("Initializing main.py");
    child = spawn("python3", ["-i", "python/main.py"]);
    print(child.pid);
    child.stdout.on("data", (data) => handleResponse(data));
}

function connectRover() {
    if(noChild()) return;
    send("connect "+textInput());
}

function send(text) {
    if(noChild()) return;
    print(`Sending ${text}`);
    child.stdin.write(text+"\n\r");
}

function stopPython() {
    if(noChild()) return;
    print("Stopping program");
    child.kill(3);
}

function walkRover() {
    if(noChild()) return;
    send("walk");
}

function textInput() {
    target = document.getElementById('text_input');
    return target.getAttribute('value');
} 

function sendRover(){
    text = textInput();
    send(text);
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
    document
        .getElementById("connect_button")
        .addEventListener("click", connectRover);
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
