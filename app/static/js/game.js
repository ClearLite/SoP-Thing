// app/static/js/game.js
document.addEventListener('DOMContentLoaded', () => {
    const gameTitle = document.getElementById('game-title');
    const matchupArea = document.getElementById('matchup-area');
    const winnerArea = document.getElementById('winner-area');

    let currentRound = 1;
    let matchups = [];
    let nextRoundContestants = [];
    let currentMatchupIndex = 0;

    function createMatchups(characters) {
        const shuffled = [...characters]; // Create a mutable copy
        const pairings = [];
        for (let i = 0; i < shuffled.length; i += 2) {
            if (shuffled[i + 1]) {
                pairings.push([shuffled[i], shuffled[i + 1]]);
            }
        }
        return pairings;
    }
    
    function renderMatchup() {
        matchupArea.innerHTML = '';
        if (currentMatchupIndex >= matchups.length) {
            // End of round
            startNextRound();
            return;
        }

        const [char1, char2] = matchups[currentMatchupIndex];
        
        matchupArea.innerHTML = `
            <div class="character-card matchup-card" data-winner-id="${char1.id}" data-loser-id="${char2.id}">
                <img src="${char1.image_url}" alt="${char1.name}">
                <div class="card-info"><h3>${char1.name}</h3><p>From: ${char1.from_where}</p></div>
            </div>
            <h2>VS</h2>
            <div class="character-card matchup-card" data-winner-id="${char2.id}" data-loser-id="${char1.id}">
                <img src="${char2.image_url}" alt="${char2.name}">
                <div class="card-info"><h3>${char2.name}</h3><p>From: ${char2.from_where}</p></div>
            </div>
        `;
        
        document.querySelectorAll('.matchup-card').forEach(card => {
            card.addEventListener('click', handleChoice);
        });
    }

    async function handleChoice(event) {
        const card = event.currentTarget;
        const winnerId = card.dataset.winnerId;
        const loserId = card.dataset.loserId;

        // Record vote on the backend
        try {
            await fetch('/api/record-vote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ winner_id: winnerId, loser_id: loserId })
            });
        } catch (error) {
            console.error("Failed to record vote:", error);
        }
        
        // Find winner object and add to next round
        const winner = matchups[currentMatchupIndex].find(c => c.id == winnerId);
        nextRoundContestants.push(winner);

        currentMatchupIndex++;
        renderMatchup();
    }

    function startNextRound() {
        if (nextRoundContestants.length === 1) {
            // We have a winner!
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
                <img src="${winner.image_url}" alt="${winner.name}">
                <div class="card-info">
                    <h2>${winner.name}</h2>
                    <p>From: ${winner.from_where}</p>
                    <a href="/" class="btn">Play Again?</a>
                </div>
            </div>
        `;
    }

    // Initial game start
    matchups = createMatchups(initialCharacters);
    renderMatchup();
});
