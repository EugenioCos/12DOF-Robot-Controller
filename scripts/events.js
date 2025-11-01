const { spawn } = require("child_process");
const nodeConsole = require("console");
const { text } = require("stream/consumers");

const DEBUG = true;

let port = "81";
let ip = "192.168.1.68";

const terminalConsole = new nodeConsole.Console(process.stdout, process.stderr);
let buffer = new Uint8Array(8192);
let bufferIndex = 0;
let imgSize = 0;
let angles = [90,90,90,90,90,90,90,90,90,90,90,90];
let sliderCoxa;
let sliderFemur;
let sliderTibia;
let iSlidersPos;
let iSlidersOrn;
let feetsTab;
let angleController;
let posOrnController;
let videoController;
let turnController;
let turnPointer;
let speedController;
let speedPointer;
let walkController;
let walkDirectionLine;
let connect_button;
let legsView;
let videoView;
let canvas;
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
            ctrlFeetTab();
        } else if(cmd == "Disconnesso"){
            connect_button.innerHTML = "Connect";
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
        videoController.style.display = (poac == 'vc' ? 'block' : 'none');
    }, 0);
}

function ctrlFeetTab(){
    // Schedule a handler to run after the modify to the tabs
    setTimeout(() => {
        let tabActive = feetsTab.querySelector('md-secondary-tab[active]');
        let feet = parseInt(tabActive.getAttribute('i-feet'));
        sliderCoxa.setAttribute('i', String(feet*3));
        sliderFemur.setAttribute('i', String(feet*3+1));
        sliderTibia.setAttribute('i', String(feet*3+2));
        updateSlider(sliderCoxa, feet*3);
        updateSlider(sliderFemur, feet*3+1);
        updateSlider(sliderTibia, feet*3+2);
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

function updateSlider(slider, i) {
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

// ------------------- WALK AND TURN CONTROL -----------------------------------------------------------------

function calculateTurnAngle(x, y) {
    xCenter = turnController.scrollWidth*3.15;
    yCenter = turnController.scrollHeight/2;
    angRad = Math.atan2(y - yCenter, x - xCenter);
    return  Math.round(angRad * (180 / Math.PI));
}

function updateTurnDirection(x, y) {
    if(noChild()) return;
    angle = calculateTurnAngle(x, y) + 180;
    if(angle > -10 && angle < 10) angle = 0;
    if(angle > 180) angle -= 360;
    if(angle > 35) angle = 35;
    if(angle < -35) angle = -35;
    updateTurnPointer(angle);
    send("setwrot "+String(angle));
}

function updateTurnPointer(angle) {
    turnPointer.style.transform = `rotate(${angle}deg)`;
}

function updateSpeed(x){
    if(noChild()) return;
    maxDelta = speedController.scrollHeight * 0.25;
    center = speedController.scrollHeight / 2;
    delta = x - center;
    if(delta > maxDelta) delta = maxDelta;
    if(delta < -maxDelta) delta = -maxDelta;
    speedPointer.style.transform = `translateY(${delta}px)`;
    scale = 0.5 - delta / (maxDelta*2);
    send("setspeed "+String(scale));
}

function calculateWalkAngle(x, y) {
    xCenter = walkController.scrollWidth/2;
    yCenter = walkController.scrollHeight/2;
    angRad = Math.atan2(y - yCenter, x - xCenter);
    return  Math.round(angRad * (180 / Math.PI));
}

function updateWalkDirection(x, y) {
    if(noChild()) return;
    angle = calculateWalkAngle(x, y);
    angleFromLeft = angle+180;
    mod90 = angleFromLeft%90;
    if(mod90 > 80) // approssimazione per eccesso
        angleFromLeft += 90 - (mod90);
    if(mod90 < 10) // approssimazione per difetto
        angleFromLeft -= mod90;
    console.log(angleFromLeft);
    updateWalkDirectionLine(angleFromLeft-90);
    send("walk "+String(angleFromLeft));
}

function updateWalkDirectionLine(angle) {
    walkDirectionLine.style.transform = `rotate(${angle}deg)`;
}

// ------------------- VIDEO VIEW ----------------------------------------------------------------------------

function showVideoView(show) {
    videoView.style.display = show ? 'block' : 'none';
    legsView.style.display = show ? 'none' : 'grid';
    send(show ? "setrecord 1" : "setrecord 0");
}

function updateVideo(array) {
    data = new Uint8Array(array);
    // parsing image size
    if(imgSize == 0) {
        let i = 0;
        let tmp = '';
        while(data[i] != 83){
            tmp += String.fromCharCode(data[i]);
            i++;
        }
        imgSize = parseInt(tmp);
        data = data.slice(i+1, data.length);
    }
    // filling buffer
    if(imgSize - bufferIndex > data.length) {
        buffer.set(data, bufferIndex);
        bufferIndex += data.length;
    } else {
        buffer.set(data.slice(0, imgSize - bufferIndex), bufferIndex);
        data = data.slice(imgSize - bufferIndex, data.length);
        bufferIndex = imgSize;
    }
    if(imgSize == 0 || bufferIndex < imgSize) return;
    // drawing image
    const blob = new Blob([buffer], {type: 'image/jpeg'});
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
    };
    img.src = url;

    if(data.length > 0) {
        buffer.set(data, 0);
        bufferIndex = data.length;
    } else bufferIndex = 0;
    imgSize = 0;
}

// ------------------- LEGS VIEW -----------------------------------------------------------------------------

function mouseToCoord(xMouse, yMouse){
    legLength = 0.1 * Math.min(window.innerWidth, window.innerHeight); // 10% = div femur or coxa lenght
    x = xMouse * 0.1 / legLength; // 0.1 = coxa or femur lenght
    y = yMouse * 0.1 / legLength; // 0.1 = coxa or femur lenght
    return [x, y];
}

function updateLeg(legView, xPage, yPage){
    if(noChild()) return;
    rect = legView.getBoundingClientRect();
    offsetY = Math.round(legView.clientHeight * 0.2);
    offsetX = Math.round(legView.clientWidth * 0.4);
    x = xPage - (rect.x + offsetX);
    y = yPage - (rect.y + offsetY) + 7;
    console.log("x: ", rect.x, rect.y);
    console.log("offset: ", offsetX, offsetY);
    console.log("coord: ", x, y);
    coords = mouseToCoord(x, y);
    feet = legView.getAttribute("feet");
    send("setfeetpos "+String(coords[0])+" "+String(-coords[1])+" "+feet);
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

function walkRover() { send("walk"); }

function turnRover() { send("turn"); }

function stopRover() { send("stop"); }

function syncRover() { send("sync"); }

function resetRover() {
    bufferIndex = 0;
    send("reset");
}

// ------------------- CONNECTION CONTROLLER ------------------------------------------------------------------

function startPython() {
    if(child && !child.killed) return;
    print("Initializing main.py");
    child = spawn("bash", ["./python/starter.bash"], {
        stdio: ["pipe", "pipe", "pipe", "pipe"]
    });
    print(`PID: ${child.pid}`);
    child.stdout.on("data", (data) => handleResponse(data));
    child.stdio[3].on("data", (data) => updateVideo(data));
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
    if(state == "Connect") connect_button.innerHTML = "Disconnect";
    else connect_button.innerHTML = "Connect";
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

// ------------------- EVENTS --------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    sliderCoxa = document.getElementById('slider_coxa');
    sliderFemur = document.getElementById('slider_femur');
    sliderTibia = document.getElementById('slider_tibia');
    iSlidersOrn = document.querySelectorAll('.orn');
    iSlidersPos = document.querySelectorAll('.pos');
    feetsTab = document.getElementById('feets-tab');
    angleController = document.getElementById('angle-controller');
    posOrnController = document.getElementById('pos-orn-controller');
    videoController = document.getElementById('video-controller');
    turnController = document.getElementById('turn-controller');
    turnPointer = turnController.querySelector('.pointer');
    speedController = document.getElementById('speed-controller');
    speedPointer = speedController.querySelector('.pointer');
    walkController = document.getElementById('walk-controller');
    walkDirectionLine = document.getElementById('walk-direction-line');
    connect_button = document.getElementById("connect_button");
    legs = document.querySelectorAll(".leg");
    tibias = document.querySelectorAll(".tibia");
    legsView = document.getElementById('legs-view');
    videoView = document.getElementById('video-view');
    canvas = document.getElementById('video-canvas');

    document
        .getElementById("start_button")
        .addEventListener("click", startPython);
    connect_button.addEventListener("click", connectRover);
    document
        .getElementById("controllers-tab")
        .addEventListener("change", event => poacTab(event.target));
    feetsTab.addEventListener("change", () => ctrlFeetTab());
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
        .getElementById("turn_button")
        .addEventListener("click", turnRover);
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
    turnController.addEventListener('click', event => {
        if(!event.target.isEqualNode(turnController)) return;
        updateTurnDirection(event.offsetX, event.offsetY);
    });
    speedController.addEventListener('click', event => {
        if(!event.target.isEqualNode(speedController)) return;
        updateSpeed(event.offsetY);
    });
    walkController.addEventListener('click', event => {
        if(!event.target.isEqualNode(walkController)) return;
        updateWalkDirection(event.offsetX, event.offsetY);
    });
    document.querySelectorAll(".leg-view").forEach(legView => {
        const handler = (event) => updateLeg(legView, event.pageX, event.pageY);
        legView.addEventListener('mousedown', () => {
            if(noChild()) return;
            legView.addEventListener('mousemove', handler);
        });
        legView.addEventListener('click', () => {
            legView.removeEventListener('mousemove', handler);
        });
    });
    document.getElementById("record-switch").addEventListener('change', (event) => {
        let inner = event.target.shadowRoot.querySelector('.switch');
        showVideoView(inner.classList.contains('selected'));
    });
});
