const mic_btn = document.querySelector('#mic');
const playback = document.querySelector('.playback');

mic_btn.addEventListener('click', ToggleMic);

let can_record = false;
let is_recording = false;

let recorder = null;

let chunks = [];

function SetupAudio() {
    console.log("Setup")
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices
            .getUserMedia({
                audio: true
            })
            .then(SetupStream)
            .catch(err => {
                console.error(err)
            });
    }
}

SetupAudio();

function SetupStream(stream) {
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = e => {
        chunks.push(e.data);
    }

    recorder.onstop = e => {
        const blob = new Blob(chunks, {type: "audio/mpeg; codecs=opus"});
        // console.log(chunks)
        SendAudioToBackend(blob);
        chunks = [];
        const audioURL = window.URL.createObjectURL(blob);
        playback.src = audioURL;
    }

    can_record = true;
}

function ToggleMic() {
    if(!can_record) return;

    is_recording = !is_recording;

    if(is_recording) {
        recorder.start();
        mic_btn.classList.add("is_recording");
    } else {
        recorder.stop();
        mic_btn.classList.remove("is_recording");
    }
}

// async function SendAudioToBackend(blob) {
//     // blob = new Blob(chunks, {type: "audio/mpeg; codecs=opus"});
//     const formData = new FormData();
//     formData.append("file", blob, "audio.mp3");

//     console.log("FormData values: ", formData.values())

//     console.log("Blob size:", blob.size); // Check blob size
//     console.log("Blob type:", blob.type); // Check blob type
//     console.log("FormData size:", formData.size); // Check FormData size
//     console.log("FormData entries:", [...formData.entries()]); // Check FormData entries


//     await fetch("http://localhost:8000/talk", {
//         method: "POST",
//         body: formData,
//         // mode: "no-cors"
//     })
//     .then(response => {
//         if(response.ok){
//             console.log("Audio sent to backend successfully: ", response);

//             //Handle
//         }else{
//             console.log(response)
//             throw new Error('Error')
//         }
//     })
//     .catch(error => {
//         console.error("Error sending audio to backend: ", error);
//     });
// }

async function SendAudioToBackend(blob) {
    const formData = new FormData();
    formData.append("file", blob, "audio.mp3");

    console.log("Blob size:", blob.size); // Check blob size
    console.log("Blob type:", blob.type); // Check blob type
    console.log("FormData size:", formData.size); // Check FormData size
    console.log("FormData entries:", [...formData.entries()]); // Check FormData entries

    try {
        const response = await fetch("http://localhost:8000/talk", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const audioBlob = await response.blob();
            const audioURL = window.URL.createObjectURL(audioBlob);
            playback.src = audioURL;
            playback.play(); // Autoplay the audio
        } else {
            throw new Error('Error sending audio to backend');
        }
    } catch (error) {
        console.error("Error sending audio to backend: ", error);
    }
}
