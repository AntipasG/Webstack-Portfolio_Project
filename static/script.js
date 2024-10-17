// static/script.js
document.addEventListener('DOMContentLoaded', function () {
    const video1 = document.getElementById('background-video1');
    const video2 = document.getElementById('background-video2');
    const video3 = document.getElementById('background-video3');
    
    let videos = [video1, video2, video3];
    let currentVideoIndex = 0;
    
    function switchVideo() {
        videos[currentVideoIndex].classList.add('hidden');
        currentVideoIndex = (currentVideoIndex + 1) % videos.length;
        videos[currentVideoIndex].classList.remove('hidden');
    }
    
    // Switch videos every 10 seconds (10000 milliseconds)
    setInterval(switchVideo, 5000);
});
