/* ============================================
   Gaming Polarisation ABM - Main Application
   ============================================ */

// ---------- 1. DOM Elements ----------
const canvas = document.getElementById('agentCanvas');
const ctx = canvas.getContext('2d');
const size = 550;

canvas.width = size;
canvas.height = size;
canvas.style.width = '100%';
canvas.style.height = 'auto';

// Parameter inputs
const numAgentsSlider = document.getElementById('numAgents');
const avgConnSlider = document.getElementById('avgConnections');
const importanceASlider = document.getElementById('importanceA');
const toleranceASlider = document.getElementById('toleranceA');
const toleranceBSlider = document.getElementById('toleranceB');
const orderSelect = document.getElementById('interactionOrder');
const ruleSelect = document.getElementById('interactionRule');
const showLinksCheckbox = document.getElementById('showLinksCheckbox');

// Buttons
const setupBtn = document.getElementById('setupBtn');
const stepBtn = document.getElementById('stepBtn');
const runBtn = document.getElementById('runBtn');
const stopBtn = document.getElementById('stopBtn');

// ---------- 2. State Variables ----------
let trendChart, opinionDistChart, attitudeADistChart, attitudeBDistChart;
let history = { ticks: [], suppo: [], neut: [], oppo: [] };
let currentAgents = [];
let currentConnections = [];
let currentWorldSize = 200;
let isRunning = false;
let updateInterval = null;

// ---------- 3. Helper Functions ----------
function updateSliderDisplays() {
    document.getElementById('numAgentsVal').innerText = numAgentsSlider.value;
    document.getElementById('avgConnectionsVal').innerText = avgConnSlider.value;
    document.getElementById('importanceAVal').innerText = parseFloat(importanceASlider.value).toFixed(2);
    document.getElementById('toleranceAVal').innerText = parseFloat(toleranceASlider.value).toFixed(2);
    document.getElementById('toleranceBVal').innerText = parseFloat(toleranceBSlider.value).toFixed(2);
}

// Event listeners for sliders
numAgentsSlider.addEventListener('input', updateSliderDisplays);
avgConnSlider.addEventListener('input', updateSliderDisplays);
importanceASlider.addEventListener('input', updateSliderDisplays);
toleranceASlider.addEventListener('input', updateSliderDisplays);
toleranceBSlider.addEventListener('input', updateSliderDisplays);
updateSliderDisplays();

// ---------- 4. API Communication ----------
async function fetchState() {
    try {
        const res = await fetch('/api/state');
        if (!res.ok) throw new Error('State fetch failed');
        return await res.json();
    } catch (e) {
        console.warn(e);
        return null;
    }
}

async function updateConfig() {
    const config = {
        num_agents: parseInt(numAgentsSlider.value),
        avg_connections: parseInt(avgConnSlider.value),
        importance_attitude_A: parseFloat(importanceASlider.value),
        tolerance_attitude_A: parseFloat(toleranceASlider.value),
        tolerance_attitude_B: parseFloat(toleranceBSlider.value),
        level_of_involvement: 0.5,
        reinforcement: 0.01,
        interaction_order: orderSelect.value,
        interaction_rule: ruleSelect.value,
        confirmation_bias: false,
        influencer_present: false
    };
    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
    } catch (e) {
        console.error(e);
    }
}

async function stepSim() {
    await fetch('/api/step', { method: 'POST' });
    await refreshDisplay();
}

async function runSim() {
    if (isRunning) return;
    isRunning = true;
    document.getElementById('loadingToast').style.display = 'block';
    await fetch('/api/run', { method: 'POST' });
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(refreshDisplay, 150);
}

async function stopSim() {
    isRunning = false;
    document.getElementById('loadingToast').style.display = 'none';
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
    await fetch('/api/stop', { method: 'POST' });
    await refreshDisplay();
}

async function resetSim() {
    await stopSim();
    await updateConfig();
    await fetch('/api/reset', { method: 'POST' });
    history = { ticks: [], suppo: [], neut: [], oppo: [] };
    if (trendChart) {
        trendChart.data.labels = [];
        trendChart.data.datasets[0].data = [];
        trendChart.data.datasets[1].data = [];
        trendChart.data.datasets[2].data = [];
        trendChart.update();
    }
    await refreshDisplay();
}

// ---------- 5. Drawing Functions ----------
function drawConnections(agents, connections, worldSize, showLinks) {
    if (!showLinks || !connections || connections.length === 0) return;

    const agentMap = new Map();
    for (let a of agents) {
        agentMap.set(a.id, { x: (a.x / worldSize) * size, y: (a.y / worldSize) * size });
    }

    for (let conn of connections) {
        const sourcePos = agentMap.get(conn.source);
        const targetPos = agentMap.get(conn.target);
        if (sourcePos && targetPos) {
            ctx.beginPath();
            ctx.moveTo(sourcePos.x, sourcePos.y);
            ctx.lineTo(targetPos.x, targetPos.y);
            ctx.strokeStyle = conn.color || 'rgba(0,0,0,0.1)';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
    }
}

function drawAgents(agents, worldSize) {
    if (!agents) return;
    const rad = 8;
    for (let a of agents) {
        const x = (a.x / worldSize) * size;
        const y = (a.y / worldSize) * size;

        function getColor() {
            if (a.opinion < -0.1) return '#4169e1';
            if (a.opinion > 0.1) return '#ff69b4';
            return '#a0a0a0';
        }

        // Left semicircle (Attitude A)
        ctx.beginPath();
        ctx.arc(x, y, rad, Math.PI / 2, Math.PI * 1.5);
        ctx.fillStyle = getColor();
        ctx.fill();

        // Right semicircle (Attitude B)
        ctx.beginPath();
        ctx.arc(x, y, rad, Math.PI * 1.5, Math.PI / 2);
        ctx.fillStyle = getColor();
        ctx.fill();

        // Border
        ctx.beginPath();
        ctx.arc(x, y, rad, 0, Math.PI * 2);
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
}

// ---------- 6. Chart Functions ----------
function initCharts() {
    const ctxTrend = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctxTrend, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'Supporters', borderColor: '#ff69b4', backgroundColor: 'rgba(255,105,180,0.1)', data: [], tension: 0.3, fill: true, pointRadius: 0, borderWidth: 1.5 },
                { label: 'Neutral', borderColor: '#a0a0a0', backgroundColor: 'rgba(160,160,160,0.1)', data: [], tension: 0.3, fill: true, pointRadius: 0, borderWidth: 1.5 },
                { label: 'Opponents', borderColor: '#4169e1', backgroundColor: 'rgba(65,105,225,0.1)', data: [], tension: 0.3, fill: true, pointRadius: 0, borderWidth: 1.5 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: false,
            plugins: {
                legend: { position: 'top', labels: { font: { size: 9, boxWidth: 10 } } }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Count', font: { size: 9 } } },
                x: { title: { display: true, text: 'Tick', font: { size: 9 } }, min: 0 }
            }
        }
    });

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
            y: { beginAtZero: true, max: 100, title: { display: true, text: 'Percentage (%)', font: { size: 9 } }, ticks: { font: { size: 8 } } },
            x: { title: { display: true, text: 'Opinion Value', font: { size: 9 } }, ticks: { font: { size: 8 } } }
        },
        plugins: { legend: { position: 'top', labels: { font: { size: 9, boxWidth: 10 } } } }
    };

    const ctxOpinion = document.getElementById('opinionDistChart').getContext('2d');
    opinionDistChart = new Chart(ctxOpinion, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Current', backgroundColor: '#4a90e2', data: [] }, { label: 'Initial', backgroundColor: '#ff9999', data: [] }] },
        options: commonOptions
    });

    const ctxA = document.getElementById('attitudeADistChart').getContext('2d');
    attitudeADistChart = new Chart(ctxA, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Current', backgroundColor: '#4a90e2', data: [] }, { label: 'Initial', backgroundColor: '#ff9999', data: [] }] },
        options: commonOptions
    });

    const ctxB = document.getElementById('attitudeBDistChart').getContext('2d');
    attitudeBDistChart = new Chart(ctxB, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Current', backgroundColor: '#4a90e2', data: [] }, { label: 'Initial', backgroundColor: '#ff9999', data: [] }] },
        options: commonOptions
    });
}

function updateTrendChart() {
    if (!trendChart) return;
    trendChart.data.labels = history.ticks;
    trendChart.data.datasets[0].data = history.suppo;
    trendChart.data.datasets[1].data = history.neut;
    trendChart.data.datasets[2].data = history.oppo;
    trendChart.update('none');
}

function updateDistributionCharts(state) {
    if (!opinionDistChart || !attitudeADistChart || !attitudeBDistChart) return;
    const initialDist = state.initial_distributions;
    const currentDist = state.current_distributions;
    if (initialDist && initialDist.bin_centers) {
        const labels = initialDist.bin_centers.map(b => b.toFixed(1));
        opinionDistChart.data.labels = labels;
        opinionDistChart.data.datasets[0].data = currentDist.opinion;
        opinionDistChart.data.datasets[1].data = initialDist.opinion;
        opinionDistChart.update('none');

        attitudeADistChart.data.labels = labels;
        attitudeADistChart.data.datasets[0].data = currentDist.attitude_a;
        attitudeADistChart.data.datasets[1].data = initialDist.attitude_a;
        attitudeADistChart.update('none');

        attitudeBDistChart.data.labels = labels;
        attitudeBDistChart.data.datasets[0].data = currentDist.attitude_b;
        attitudeBDistChart.data.datasets[1].data = initialDist.attitude_b;
        attitudeBDistChart.update('none');
    }
}

// ---------- 7. Main Display Update ----------
async function refreshDisplay() {
    const state = await fetchState();
    if (!state) return;

    currentAgents = state.individuals;
    currentConnections = state.connections || [];
    currentWorldSize = state.config?.world_size || 200;
    const stats = state.stats;
    const total = stats.oppo + stats.neut + stats.suppo;

    // Update agent count
    document.getElementById('agentCount').innerText = currentAgents.length;

    // Update statistics
    document.getElementById('suppoCount').innerText = stats.suppo;
    document.getElementById('neutCount').innerText = stats.neut;
    document.getElementById('oppoCount').innerText = stats.oppo;
    document.getElementById('suppoPct').innerText = total ? `(${((stats.suppo / total) * 100).toFixed(1)}%)` : '(0%)';
    document.getElementById('neutPct').innerText = total ? `(${((stats.neut / total) * 100).toFixed(1)}%)` : '(0%)';
    document.getElementById('oppoPct').innerText = total ? `(${((stats.oppo / total) * 100).toFixed(1)}%)` : '(0%)';
    document.getElementById('corrValue').innerText = stats.correlation.toFixed(3);
    document.getElementById('heteroValue').innerText = stats.heterogeneity.toFixed(3);
    document.getElementById('consonanceValue').innerText = (stats.consonance || 0).toFixed(3);
    document.getElementById('tickValue').innerText = state.tick;
    document.getElementById('maxTicksValue').innerText = state.config?.max_ticks || 1000;

    // Clear and redraw canvas
    ctx.clearRect(0, 0, size, size);

    // Draw grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 4; i++) {
        const pos = i * size / 4;
        ctx.beginPath();
        ctx.moveTo(pos, 0);
        ctx.lineTo(pos, size);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, pos);
        ctx.lineTo(size, pos);
        ctx.stroke();
    }

    drawConnections(currentAgents, currentConnections, currentWorldSize, showLinksCheckbox.checked);
    drawAgents(currentAgents, currentWorldSize);

    // Update history and trend chart
    if (state.tick !== history.ticks[history.ticks.length - 1]) {
        history.ticks.push(state.tick);
        history.suppo.push(stats.suppo);
        history.neut.push(stats.neut);
        history.oppo.push(stats.oppo);
        if (history.ticks.length > 200) {
            history.ticks.shift();
            history.suppo.shift();
            history.neut.shift();
            history.oppo.shift();
        }
        updateTrendChart();
    }

    updateDistributionCharts(state);
}

// ---------- 8. Event Listeners ----------
showLinksCheckbox.addEventListener('change', () => refreshDisplay());
setupBtn.onclick = resetSim;
stepBtn.onclick = async () => {
    await stopSim();
    await stepSim();
};
runBtn.onclick = runSim;
stopBtn.onclick = stopSim;

// ---------- 9. Initialization ----------
window.addEventListener('load', async () => {
    initCharts();
    await updateConfig();
    await resetSim();
});