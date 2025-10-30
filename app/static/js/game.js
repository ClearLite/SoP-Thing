// app/static/js/game.js
document.addEventListener('DOMContentLoaded', () => {
    const gameTitle = document.getElementById('game-title');
    const matchupArea = document.getElementById('matchup-area');
    const winnerArea = document.getElementById('winner-area');
    const modal = document.getElementById('image-modal');
    const modalCloseBtn = document.querySelector('.modal-close-btn');
    const modalImageGallery = document.getElementById('modal-image-gallery');
    const modalNoImagesMsg = document.getElementById('modal-no-images-msg');

    let currentRound = 1;
    let matchups = [];
    let nextRoundContestants = [];
    let currentMatchupIndex = 0;

    function createMatchups(characters) {
        const pairings = [];
        for (let i = 0; i < characters.length; i += 2) {
            if (characters[i + 1]) {
                pairings.push([characters[i], characters[i + 1]]);
            }
        }
        return pairings;
    }
    
    function renderMatchup() {
        matchupArea.innerHTML = '';
        if (currentMatchupIndex >= matchups.length) {
            startNextRound();
            return;
        }

        const [char1, char2] = matchups[currentMatchupIndex];
        
        matchupArea.innerHTML = `
            <div class="matchup-container">
                <div class="character-card matchup-card" data-winner-id="${char1.id}" data-loser-id="${char2.id}">
                    <div class="image-container">
                        <img src="${char1.image_url}" alt="${char1.name}">
                    </div>
                    <div class="card-info"><h3>${char1.name}</h3></div>
                </div>
                <button class="btn btn-view-images" data-char-index="0"><i class="fas fa-images"></i> View Images</button>
            </div>
            <h2 class="vs-text">VS</h2>
            <div class="matchup-container">
                <div class="character-card matchup-card" data-winner-id="${char2.id}" data-loser-id="${char1.id}">
                    <div class="image-container">
                        <img src="${char2.image_url}" alt="${char2.name}">
                    </div>
                    <div class="card-info"><h3>${char2.name}</h3></div>
                </div>
                <button class="btn btn-view-images" data-char-index="1"><i class="fas fa-images"></i> View Images</button>
            </div>
        `;
        
        document.querySelectorAll('.matchup-card').forEach(card => {
            card.addEventListener('click', handleChoice);
        });

        document.querySelectorAll('.btn-view-images').forEach(button => {
            button.addEventListener('click', handleViewImages);
        });
    }

    async function handleChoice(event) {
        const card = event.currentTarget;
        const winnerId = card.dataset.winnerId;
        const loserId = card.dataset.loserId;

        try {
            await fetch('/api/record-vote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ winner_id: winnerId, loser_id: loserId })
            });
        } catch (error) {
            console.error("Failed to record vote:", error);
        }
        
        const winner = matchups[currentMatchupIndex].find(c => c.id == winnerId);
        nextRoundContestants.push(winner);

        currentMatchupIndex++;
        renderMatchup();
    }

    function handleViewImages(event) {
        const charIndex = parseInt(event.currentTarget.dataset.charIndex, 10);
        const character = matchups[currentMatchupIndex][charIndex];
        openImageModal(character);
    }

    function openImageModal(character) {
        // Clear previous content
        modalImageGallery.innerHTML = '';
        modalNoImagesMsg.style.display = 'none';

        if (character.additional_image_urls && character.additional_image_urls.length > 0) {
            character.additional_image_urls.forEach(url => {
                const img = document.createElement('img');
                img.src = url;
                modalImageGallery.appendChild(img);
            });
        } else {
            modalNoImagesMsg.style.display = 'block';
        }
        modal.style.display = 'flex';
    }

    function closeImageModal() {
        modal.style.display = 'none';
    }

    function startNextRound() {
        if (nextRoundContestants.length === 1) {
            displayWinner(nextRoundContestants[0]);
            return;
        }

        currentRound++;
        matchups = createMatchups(nextRoundContestants);
        nextRoundContestants = [];
        currentMatchupIndex = 0;
        
        gameTitle.textContent = `Round ${currentRound}`;
        renderMatchup();
    }

    function displayWinner(winner) {
        gameTitle.textContent = '🏆 Grand Champion! 🏆';
        matchupArea.style.display = 'none';
        winnerArea.style.display = 'block';
        winnerArea.innerHTML = `
            <div class="character-card winner-card">
                 <div class="image-container">
                    <img src="${winner.image_url}" alt="${winner.name}">
                </div>
                <div class="card-info">
                    <h2>${winner.name}</h2>
                    <p>From: ${winner.from_where}</p>
                    <a href="/" class="btn">Play Again?</a>
                </div>
            </div>
        `;
    }
    
    // Modal event listeners
    modalCloseBtn.addEventListener('click', closeImageModal);
    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            closeImageModal();
        }
    });

    // Initial game start
    matchups = createMatchups(initialCharacters);
    renderMatchup();
});
