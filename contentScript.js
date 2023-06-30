let markersShown = false;  // State to track whether markers are shown or hidden

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.command === "markVideo") {
        hideMarkers();
        showMarkers(request.timestamps, "#57DD73");
        showMarkers(request.extended_timestamps, "#1EEAFF");
        showMarkers(request.similar_timestamps, "#FF9600");

        // Toggle the state
        markersShown = true;
        console.log("done showing")
    } else if (request.command === "removeMarkers") {
        hideMarkers();
        markersShown = false;
    }
});


function hideMarkers() {
    // If markers are currently shown, hide them
    let markers = document.querySelectorAll('.marker');
    markers.forEach(function(marker) {
        marker.style.display = 'none';
    });
}

function showMarkers(timestamps, color) {
    // If markers are currently hidden, show them
    let videoElement = document.querySelector("video");
    let progressBar = document.querySelector('.ytp-progress-bar');

    let videoDuration = videoElement.duration;
    timestamps.forEach(function(timestamp) {
        if (timestamp === 0){
            console.log("none found");
            //error("No occurances found (not 100% accurate)")
            return;
        };

        let position = (timestamp / videoDuration)* 100;
        // Create the marker
        let marker = document.createElement('div');
        marker.className = 'marker';  // Add a class to the marker for easy selection
        marker.style.position = 'absolute';
        marker.style.height = '100%';
        marker.style.width = '2px';
        marker.style.backgroundColor = color;
        marker.style.left = `${position}%`;

        // Append the marker to the progress bar
        progressBar.appendChild(marker);
    });
}
