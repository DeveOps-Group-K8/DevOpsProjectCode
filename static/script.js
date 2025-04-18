let secretNumber = Math.floor(Math.random() * 100) + 1;
        let attempts = 0;

        function checkGuess() {
            let userGuess = document.getElementById("guess").value;
            let message = document.getElementById("message");

            if (userGuess == secretNumber) {
                message.innerHTML = "🎉 Congratulations! You guessed the number in " + attempts + " attempts!";
                message.style.color = "green";
                document.getElementById("submitBtn").disabled = true;
            } else if (userGuess > secretNumber) {
                message.innerHTML = "📉 Too high! Try again.";
                message.style.color = "red";
            } else {
                message.innerHTML = "📈 Too low! Try again.";
                message.style.color = "red";
            }
            attempts++;
        }

        function restartGame() {
            secretNumber = Math.floor(Math.random() * 100) + 1;
            attempts = 0;
            document.getElementById("message").innerHTML = "";
            document.getElementById("guess").value = "";
            document.getElementById("submitBtn").disabled = false;
        }

        function launchConfetti() {
            const confettiSettings = { particleCount: 100, spread: 70, origin: { y: 0.6 } };
            confetti(confettiSettings);
        }
        if (correctGuess) {
            launchConfetti();
        }

const successSound = new Audio("{{ url_for('static', filename='Running.mp3') }}");
const errorSound = new Audio("{{ url_for('static', filename='JustdeyPlay.mp3') }}");

function checkGuess() {
    let userGuess = document.getElementById("guess").value;
    if (userGuess == correctNumber) {
        successSound.play();
        launchConfetti();  // 🎉 Confetti effect
    } else {
        errorSound.play();
    }
}

window.onload = function () {
    // Check if the first item in the leaderboard has a rank of 1
    let firstPlace = document.querySelector('.leaderboard li');
    if (firstPlace && firstPlace.textContent.includes('🥇')) {
        playCelebrationSound();  // Play sound for the top player
    }
};

