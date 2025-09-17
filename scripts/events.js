const { exec, spawn } = require("child_process");
const nodeConsole = require("console");
const { connect } = require("net");
const { text } = require("stream/consumers");

const DEBUG = true;

let port = "81";
let ip = "192.168.1.68";

const terminalConsole = new nodeConsole.Console(process.stdout, process.stderr);
let angles = [90,90,90,90,90,90,90,90,90,90,90,90];
let sliderCoxa;
let sliderFemur;
let sliderTibia;
let iSlidersPos;
let iSlidersOrn;
let angleController;
let posOrnController;
let walkTurnController;
let walkDirectionLine;
let connect_button;
let legs;
let tibias;
let child;

function print(data) {
    if(!DEBUG) return;
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

// ------------------- MESSAGES ELABORATION ------------------------------------------------------------------

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
            for(let i = 0; i < 12; i++) {
                angles[i] = parseInt(words.pop());
            }
            updateLegs([angles[1], angles[7], angles[4], angles[10]]);
            updateTibias([angles[2], angles[8], angles[5], angles[11]]);
            tabs = document.getElementById('ctrl_feet_tab');
            ctrlFeetTab(tabs, true);
        }
    }
}

// ------------------- TABS ---------------------------------------------------------------------------------

function poacTab(target) {
    // Schedule a handler to run after the modify to the tabs
    setTimeout(() => {
        let tabActive = target.querySelector('md-secondary-tab[active]');
        let poac = tabActive.getAttribute('po-ac');
        angleController.style.display = (poac == 'ac' ? 'block' : 'none');
        posOrnController.style.display = (poac == 'po' ? 'block' : 'none');
    }, 0);
}

function ctrlFeetTab(target, by_fraction){
    // Schedule a handler to run after the modify to the tabs
    setTimeout(() => {
        let tabActive = target.querySelector('md-secondary-tab[active]');
        let feet = parseInt(tabActive.getAttribute('i-feet'));
        sliderCoxa.setAttribute('i', String(feet*3));
        sliderFemur.setAttribute('i', String(feet*3+1));
        sliderTibia.setAttribute('i', String(feet*3+2));
        updateSlider(sliderCoxa, feet*3, by_fraction);
        updateSlider(sliderFemur, feet*3+1, by_fraction);
        updateSlider(sliderTibia, feet*3+2, by_fraction);
    }, 0);
}

function posOrnTab(target){
    // Schedule a handler to run after the modify to the tabs
    setTimeout(() => {
        let tabActive = target.querySelector('md-secondary-tab[active]');
        let posOrn = tabActive.getAttribute('pos-orn');
        iSlidersPos.forEach((elem) => {
            if(posOrn == "pos") elem.style.display = 'block';
            else elem.style.display = 'none';
        });
        iSlidersOrn.forEach((elem) => {
            if(posOrn == "orn") elem.style.display = 'block';
            else elem.style.display = 'none';
        });
    }, 0);
}

function updateSlider(slider, i, by_fraction) {
    if((i + 1) % 3 != 0) limit = parseInt(slider.getAttribute('max'));
    else limit = parseInt(slider.getAttribute('min'));
    if(Math.abs(angles[i]) - Math.abs(limit) > 0) return;

    let fraction = Math.abs(angles[i] / limit);
    if(fraction > 1) return;
    let container = slider.shadowRoot.querySelector('.container');
    if((i + 1) % 3 == 0) fraction = 1 - fraction;
    container.style.setProperty('--_end-fraction', fraction);

    let input = slider.shadowRoot.querySelector('input');
    input.value = angles[i];
}

// ------------------- CONNECTION CONTROLLER ------------------------------------------------------------------

function startPython() {
    print("Initializing main.py");
    child = spawn("python3", ["-i", "python/main.py"]);
    print(`PID: ${child.pid}`);
    child.stdout.on("data", (data) => handleResponse(data));
}

function connectRover() {
    if(noChild()) return;
    let state = connect_button.innerHTML;
    if(state == "Connect") send("connect "+ip+" "+port);
    else {
        send("disconnect");
        changeConnectButton();
    }
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

function changeConnectButton(){
    let state = connect_button.innerHTML;
    if(state == "Connetti") connect_button.innerHTML = "Disconnect";
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

// ------------------- LEGS VIEW -----------------------------------------------------------------------------

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

// ------------------- WALK AND TURN CONTROL -----------------------------------------------------------------

function calculateAngle(x, y) {
    xCenter = walkTurnController.scrollWidth/2;
    yCenter = walkTurnController.scrollHeight/2;
    angRad = Math.atan2(y - yCenter, x - xCenter);
    return  Math.round(angRad * (180 / Math.PI));
}

function updateWalkDirection(x, y) {
    if(noChild()) return;
    angle = calculateAngle(x, y);
    angleFromLeft = angle + 180;
    walkDirectionLine.style.transform = `rotate(${angleFromLeft - 90}deg)`;
    send("walk "+String(angleFromLeft));
}

// ------------------- EVENTS --------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    sliderCoxa = document.getElementById('slider_coxa');
    sliderFemur = document.getElementById('slider_femur');
    sliderTibia = document.getElementById('slider_tibia');
    iSlidersOrn = document.querySelectorAll('.orn');
    iSlidersPos = document.querySelectorAll('.pos');
    angleController = document.getElementById('angle-controller');
    posOrnController = document.getElementById('pos-orn-controller');
    walkTurnController = document.getElementById('walk-turn-controller');
    walkDirectionLine = document.getElementById('walk-direction-line');
    connect_button = document.getElementById("connect_button");
    legs = document.querySelectorAll(".leg");
    tibias = document.querySelectorAll(".tibia");


    document
        .getElementById("start_button")
        .addEventListener("click", startPython);
    connect_button.addEventListener("click", connectRover);
    document
        .getElementById("poac_tab")
        .addEventListener("change", event => poacTab(event.target));
    document
        .getElementById("ctrl_feet_tab")
        .addEventListener("change", event => ctrlFeetTab(event.target, false));
    document
        .getElementById("pos_orn_tab")
        .addEventListener("change", event => posOrnTab(event.target));
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
    document
        .querySelectorAll('md-slider')
        .forEach((slider) => {
                slider.addEventListener('input', (event) => {
                target = event.currentTarget;
                let cmd = target.getAttribute('cmd');
                let i = target.getAttribute('i');
                input = target.shadowRoot.querySelector('input');
                let value = input.ariaValueText;
                if(cmd == "setang"){
                    angles[i] = parseInt(value);
                    updateLegs([angles[1], angles[7], angles[4], angles[10]]);
                    updateTibias([angles[2], angles[8], angles[5], angles[11]]);
                }
                send(`${cmd} ${i} ${value}`);
            });
    });
    walkTurnController.addEventListener('click', event => {
        if(!event.target.isEqualNode(walkTurnController)) return;
        updateWalkDirection(event.offsetX, event.offsetY);
    });
});
