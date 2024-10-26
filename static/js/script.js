const menuToggle = document.getElementById('menu-toggle');
const navbar = document.getElementById('navbar');

menuToggle.addEventListener('click', () => {
    navbar.classList.toggle('show'); 
});

function updateStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temp-value').innerText = data.tempThreshold;
            document.getElementById('phone-number-value').innerText = data.phoneNumber;
            document.getElementById('arduino-status-value').innerText = data.arduinoStatus;
            document.getElementById('gsm-status-value').innerText = data.gsmStatus;
        })
        .catch(error => console.error('Error fetching status:', error));
}

setInterval(updateStatus, 5000);
