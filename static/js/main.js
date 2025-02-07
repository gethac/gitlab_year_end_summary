document.addEventListener('DOMContentLoaded', function () {
    const links = document.querySelectorAll('.summary-link');
    links.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const target = this.getAttribute('href');
            document.querySelector(target).scrollIntoView({behavior: 'smooth'});
        });
    });
});

window.addEventListener('resize', function () {
    resize()
});

function resize() {
    var width = window.innerWidth;
    if (width >= 1000) {
        document.querySelector('.container').classList.add('desktop-styles');
        document.querySelector('.container').classList.remove('mobile-styles');
    } else {
        document.querySelector('.container').classList.add('mobile-styles');
        document.querySelector('.container').classList.remove('desktop-styles');
    }
}

resize()


const audio = document.getElementById('background-music');
const playButton = document.getElementById('play-button');

// 检查音频是否已经播放
if (localStorage.getItem('musicPlaying') === 'true') {
    musicPlay()
}

playButton.addEventListener('click', () => {
    musicPlay()
    localStorage.setItem('musicPlaying', 'true');
});

// 监听页面卸载事件，确保音乐持续播放
window.addEventListener('beforeunload', () => {
    audio.pause();
});

function musicPlay() {
    if (audio.paused) {
        audio.play().catch(error => {
            console.error("Playback failed:", error);
        })
        playButton.classList.add('music_open');
        playButton.classList.remove('music_close');
    } else {
        audio.pause();
        playButton.classList.add('music_close');
        playButton.classList.remove('music_open');
    }
}
