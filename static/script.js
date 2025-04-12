document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('summaryForm');
    const urlInput = document.getElementById('urlInput');
    const resultBox = document.getElementById('result');
    const summaryText = document.getElementById('summaryText');
    const errorBox = document.getElementById('error');
    const errorText = document.getElementById('errorText');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        resultBox.style.display = 'none';
        errorBox.style.display = 'none';

        const url = urlInput.value.trim();
        try {
            const response = await fetch("/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                body: new URLSearchParams({ url })
            });
            const data = await response.json();
            if (data.summary) {
                summaryText.innerText = data.summary;
                resultBox.style.display = 'block';
            } else if (data.error) {
                errorText.innerText = data.error;
                errorBox.style.display = 'block';
            }
        } catch (err) {
            errorText.innerText = err.message;
            errorBox.style.display = 'block';
        }
    });

    // Easter egg interactions
    document.getElementById('tile1').addEventListener('click', () => {
        alert('🐣 Surprise! You found the first Easter egg!');
    });

    document.getElementById('tile2').addEventListener('click', () => {
        const egg = document.createElement('div');
        egg.textContent = '🥚';
        egg.style.position = 'fixed';
        egg.style.left = Math.random() * 100 + 'vw';
        egg.style.top = '-50px';
        egg.style.fontSize = '2rem';
        egg.style.animation = 'drop 3s linear forwards';
        document.body.appendChild(egg);
    });

    document.getElementById('tile3').addEventListener('click', () => {
        document.body.style.transition = 'background-color 0.5s';
        document.body.style.backgroundColor = '#ffeb3b';
        setTimeout(() => {
            document.body.style.backgroundColor = ''; // Reset background color after a short delay
        }, 1000);
    });
});