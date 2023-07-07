document.getElementById('markButton').onclick = function() {
    processVideo('markVideo');
};

document.getElementById('RemoveButton').onclick = function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {command: "removeMarkers"});
    });
};

function processVideo(command) {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        let input_text = document.getElementById('myText');

        if (!input_text.value.trim()) {
            alert('Please enter text in the input box');
            return;
        }

        let url = tabs[0].url;  // Get the URL of the current tab

        // Send the URL to the server
        fetch('http://localhost:3000/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({url: url, text: input_text.value})
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            chrome.tabs.sendMessage(tabs[0].id, 
                {command: command,
                     timestamps: data.timestamps,
                      extended_timestamps: data.extended_timestamps,
                       identical_phoneme_timestamps: data.phoneme_matches,
                        similar_phoneme_timestamps: data.similar_phonemes});
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
}
