const gridEl = document.getElementById('game-grid');
const viewportEl = document.getElementById('game-viewport');
const libraryEl = document.getElementById('library-hub');
const gameFrame = document.getElementById('gameFrame');
const searchInput = document.getElementById('gameSearch');
const statusText = document.getElementById('statusText');
const statusDot = document.querySelector('.dot');

let allGames = [];
let baseUrls = [];
let currentBlobUrl = null;
let activeBaseUrl = ""; 
let isCdnAvailable = false;

const normalize = (name) => name.toLowerCase().trim().replace(/\s+/g, '-');

/**
 * Connectivity Test:
 * Determines if we can offload assets to a CDN.
 */
async function checkConnectivity() {
    statusText.textContent = "Checking bypass routes...";
    
    const tests = [
        { name: 'jsDelivr', url: 'https://cdn.jsdelivr.net/gh/phexusmath/phexusmath.github.io@main/index.html', base: 'jsdelivr' },
        { name: 'GitHack', url: 'https://raw.githack.com/phexusmath/phexusmath.github.io/main/index.html', base: 'githack' }
    ];

    for (let test of tests) {
        try {
            const response = await fetch(test.url, { 
                method: 'GET', 
                cache: 'no-cache' 
            });

            if (response.ok) {
                const text = await response.text();
                if (text.includes('<html') || text.includes('<!DOCTYPE')) {
                    if (test.base) {
                        activeBaseUrl = test.base;
                        isCdnAvailable = true;
                    }
                    statusText.textContent = `${test.name} Linked`;
                    statusDot.className = 'dot online';
                    return;
                }
            }
        } catch (e) { 
            console.warn(`${test.name} failed or blocked by CORS/Network.`); 
        }
    }

    statusText.textContent = "Local Mode Only";
    statusDot.style.backgroundColor = "#ff9800";
}

/**
 * Find base URL for a game and convert to the active CDN format
 */
function getGameBaseUrl(gameName) {
    const gameEntry = baseUrls.find(b => b.name === gameName);
    if (!gameEntry) return null;

    const jsdelivrUrl = gameEntry.url;
    
    if (activeBaseUrl === 'githack') {
        // Convert from https://cdn.jsdelivr.net/gh/owner/repo@ref/path
        // to https://raw.githack.com/owner/repo/ref/path
        return jsdelivrUrl
            .replace('https://cdn.jsdelivr.net/gh/', 'https://raw.githack.com/')
            .replace('@', '/');
    }
    
    // Otherwise return the jsdelivr URL as-is
    return jsdelivrUrl;
}

/**
 * Unified Loader
 * Uses the URL from list.json and respects /complete/ vs /files/ paths
 */
/**
 * Unified Loader
 * Uses the URL from list.json and respects /complete/ vs /files/ paths
 */
async function loadGame(game) {
    // 1. Use the actual URL from the JSON
    let targetUrl = game.url;
    if (!targetUrl.endsWith('/')) targetUrl += '/';

    // 2. Identify if this is a "complete" game or a "files" game
    const isComplete = targetUrl.includes('/complete/');

    try {
        // Fetch the index.html from the specific path defined in the JSON
        const res = await fetch(`${targetUrl}index.html`);
        if (!res.ok) throw new Error(`File not found at ${targetUrl}`);
        
        let html = await res.text();

        // 3. Conditional Injection
        if (isCdnAvailable) {
            let cdnUrl;
            
            if (isComplete) {
                // For /complete/ games, use phexusmath.github.io/complete/game-name
                const gameName = normalize(game.name);
                cdnUrl = `https://phexusmath.github.io/complete/${gameName}/`;
            } else {
                // For /files/ games, use the base_urls lookup
                cdnUrl = getGameBaseUrl(game.name);
            }
            
            if (cdnUrl) {
                const baseTag = `<base href="${cdnUrl}">`;
                
                // Remove all existing base tags
                html = html.replace(/<base[^>]*>/gi, '');
                
                // Inject the correct base tag into <head>
                html = html.includes('<head>') 
                    ? html.replace('<head>', `<head>\n    ${baseTag}`) 
                    : baseTag + html;
                console.log(`Injecting base: ${cdnUrl}`);
            }
        } else {
            console.log(`CDN not available - No base injection.`);
        }

        // 4. Blob Launch
        if (currentBlobUrl) URL.revokeObjectURL(currentBlobUrl);
        const blob = new Blob([html], { type: 'text/html' });
        currentBlobUrl = URL.createObjectURL(blob);

        libraryEl.style.display = 'none';
        viewportEl.style.display = 'flex';
        gameFrame.src = currentBlobUrl;

    } catch (err) {
        console.error("Load Error:", err);
        alert(`Error: Could not load game from ${targetUrl}index.html`);
    }
}

async function init() {
    await checkConnectivity();

    try {
        // Load base_urls.json
        const baseUrlsResponse = await fetch('base_urls.json');
        if (baseUrlsResponse.ok) {
            baseUrls = await baseUrlsResponse.json();
        }

        // Load list.json
        const response = await fetch('list.json');
        if (!response.ok) throw new Error('list.json not found');
        
        const games = await response.json();
        
        allGames = games.sort((a, b) => a.name.localeCompare(b.name));
        renderGrid(allGames);
    } catch (err) {
        gridEl.innerHTML = `<p style="color:white;">Error: Could not load list.json</p>`;
    }
}

function renderGrid(games) {
    gridEl.innerHTML = '';
    gridEl.classList.remove('loading-state');
    
    games.forEach(game => {
        const card = document.createElement('div');
        card.className = 'game-card';
        card.innerHTML = `<h3>${game.name}</h3> <i class="fas fa-play-circle"></i>`;
        card.onclick = () => loadGame(game);
        gridEl.appendChild(card);
    });
}

// Search Filter
searchInput.oninput = (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allGames.filter(g => g.name.toLowerCase().includes(term));
    renderGrid(filtered);
};

// Fullscreen
document.getElementById('fullscreen-btn').onclick = () => {
    if (gameFrame.requestFullscreen) gameFrame.requestFullscreen();
    else if (gameFrame.webkitRequestFullscreen) gameFrame.webkitRequestFullscreen();
};

// Back to Hub
document.getElementById('back-to-hub').onclick = () => {
    viewportEl.style.display = 'none';
    libraryEl.style.display = 'block';
    gameFrame.src = 'about:blank';
};

init();