/* ============================================
   TruthLens — Application Logic
   ============================================ */

const API_URL = "http://localhost:5000/api";

// --- Sample Texts ---
const SAMPLES = {
    real: `The Federal Reserve announced a quarter-point interest rate increase today, citing ongoing inflationary pressures in the economy. Fed Chair Jerome Powell stated that the decision was made after careful consideration of current economic indicators, including employment data and consumer spending patterns. The move was largely anticipated by financial markets, with major indices showing minimal reaction to the announcement. Economists expect the central bank to continue monitoring inflation closely before making any further adjustments to monetary policy.`,

    fake: `BREAKING: Scientists discover that drinking a special combination of lemon juice and baking soda can completely CURE cancer within 48 hours!! The medical establishment has been HIDING this information for DECADES because they make BILLIONS from chemotherapy treatments! Share this before they DELETE it!! Major hospitals are FURIOUS that this secret is finally out! A leaked document from the WHO confirms this home remedy is 100% effective but Big Pharma has been suppressing it!! EXPOSED!!`,

    ai: `In the rapidly evolving landscape of artificial intelligence, it is important to note that these technologies are fundamentally reshaping how we interact with the digital world. Furthermore, the implications of these advancements extend far beyond mere technological innovation, touching upon every aspect of our daily lives. Moreover, the convergence of machine learning algorithms and big data analytics has created unprecedented opportunities for organizations across various sectors. Additionally, it is worth mentioning that the ethical considerations surrounding AI deployment have become increasingly significant. Subsequently, policymakers and industry leaders must work collaboratively to establish comprehensive frameworks that balance innovation with responsible development. In conclusion, the transformative potential of artificial intelligence represents both a remarkable opportunity and a significant challenge for society as a whole.`,
};

// --- DOM Elements ---
const textInput = document.getElementById("text-input");
const urlInput = document.getElementById("url-input");
const charCount = document.getElementById("char-count");
const analyzeBtn = document.getElementById("analyze-btn");
const btnLoader = document.getElementById("btn-loader");
const resultsContainer = document.getElementById("results-container");

// Tabs
const tabPaste = document.getElementById("tab-paste");
const tabUrl = document.getElementById("tab-url");
const inputPaste = document.getElementById("input-paste");
const inputUrl = document.getElementById("input-url");

// Results elements
const overallBadge = document.getElementById("overall-badge");
const overallRing = document.getElementById("overall-ring");
const overallScoreValue = document.getElementById("overall-score-value");
const overallVerdict = document.getElementById("overall-verdict");
const overallDescription = document.getElementById("overall-description");

const fakeBar = document.getElementById("fake-bar");
const fakeScore = document.getElementById("fake-score");
const fakeVerdict = document.getElementById("fake-verdict");
const fakeConfidence = document.getElementById("fake-confidence");
const fakeDetails = document.getElementById("fake-details");

const aiBar = document.getElementById("ai-bar");
const aiScore = document.getElementById("ai-score");
const aiVerdict = document.getElementById("ai-verdict");
const aiConfidence = document.getElementById("ai-confidence");
const aiDetails = document.getElementById("ai-details");

const metricsGrid = document.getElementById("metrics-grid");
const toggleMetrics = document.getElementById("toggle-metrics");

// --- Inject SVG Gradient for Ring ---
function injectSVGDefs() {
    const svg = document.querySelector(".score-ring");
    if (!svg) return;
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
        <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#6366f1"/>
            <stop offset="100%" stop-color="#06b6d4"/>
        </linearGradient>
    `;
    svg.prepend(defs);
}

// --- Tab Switching ---
tabPaste.addEventListener("click", () => {
    tabPaste.classList.add("active");
    tabUrl.classList.remove("active");
    inputPaste.classList.remove("hidden");
    inputUrl.classList.add("hidden");
});

tabUrl.addEventListener("click", () => {
    tabUrl.classList.add("active");
    tabPaste.classList.remove("active");
    inputUrl.classList.remove("hidden");
    inputPaste.classList.add("hidden");
});

// --- Character Count ---
textInput.addEventListener("input", () => {
    const len = textInput.value.length;
    charCount.textContent = `${len.toLocaleString()} characters`;
});

// --- Sample Buttons ---
document.querySelectorAll(".sample-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        const sampleType = btn.dataset.sample;
        textInput.value = SAMPLES[sampleType] || "";
        textInput.dispatchEvent(new Event("input"));
        // Switch to paste tab
        tabPaste.click();
        textInput.focus();
    });
});

// --- Analyze ---
analyzeBtn.addEventListener("click", async () => {
    const activeTab = tabPaste.classList.contains("active") ? "paste" : "url";
    let text = "";

    if (activeTab === "paste") {
        text = textInput.value.trim();
    } else {
        // URL mode — for now, prompt user
        const url = urlInput.value.trim();
        if (!url) {
            showError("Please enter a URL.");
            return;
        }
        text = `[URL analysis]: ${url}\nNote: URL content extraction is a placeholder. Please paste the article text directly for best results.`;
    }

    if (!text || text.length < 20) {
        showError("Please enter at least 20 characters of text to analyze.");
        return;
    }

    await analyzeText(text);
});

// Keyboard shortcut
textInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        analyzeBtn.click();
    }
});

async function analyzeText(text) {
    setLoading(true);

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Server error");
        }

        const data = await response.json();
        displayResults(data);
    } catch (err) {
        console.error("Analysis error:", err);
        showError(
            err.message.includes("Failed to fetch")
                ? "Cannot connect to the server. Make sure the backend is running on http://localhost:5000"
                : err.message
        );
    } finally {
        setLoading(false);
    }
}

function setLoading(loading) {
    if (loading) {
        analyzeBtn.classList.add("loading");
        btnLoader.classList.remove("hidden");
        analyzeBtn.disabled = true;
    } else {
        analyzeBtn.classList.remove("loading");
        btnLoader.classList.add("hidden");
        analyzeBtn.disabled = false;
    }
}

function showError(message) {
    // Simple error display using alert for now, could be enhanced with toast
    alert(message);
}

// --- Display Results ---
function displayResults(data) {
    resultsContainer.classList.remove("hidden");

    // Scroll to results
    setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);

    // --- Overall ---
    const overall = data.overall;
    animateCounter(overallScoreValue, overall.score);

    // Ring animation
    const circumference = 2 * Math.PI * 52; // radius 52
    const offset = circumference - (overall.score / 100) * circumference;
    setTimeout(() => {
        overallRing.style.strokeDashoffset = offset;
    }, 100);

    // Update ring gradient color based on risk
    updateRingColor(overall.score);

    overallVerdict.textContent = overall.verdict;
    overallDescription.textContent = overall.label;

    // Badge
    overallBadge.textContent = overall.verdict;
    overallBadge.className = "result-badge";
    if (overall.score >= 70) overallBadge.classList.add("badge-risk-high");
    else if (overall.score >= 45) overallBadge.classList.add("badge-risk-medium");
    else if (overall.score >= 25) overallBadge.classList.add("badge-risk-low");
    else overallBadge.classList.add("badge-risk-minimal");

    // --- Fake News ---
    const fake = data.fake_news;
    if (fake.score >= 0) {
        setTimeout(() => {
            fakeBar.style.width = `${fake.score}%`;
        }, 200);
        fakeBar.className = "score-bar-fill " + getBarClass(fake.score);
        fakeScore.textContent = `${fake.score}%`;
        fakeScore.className = "score-value " + getScoreClass(fake.score);
        fakeVerdict.textContent = fake.verdict;
        fakeVerdict.className = "result-verdict " + getScoreClass(fake.score);
        fakeConfidence.textContent = `Confidence: ${fake.confidence}`;
        fakeDetails.textContent = fake.details;
    } else {
        fakeScore.textContent = "N/A";
        fakeVerdict.textContent = fake.verdict;
        fakeDetails.textContent = fake.details;
    }

    // --- AI Detection ---
    const ai = data.ai_detection;
    setTimeout(() => {
        aiBar.style.width = `${ai.score}%`;
    }, 300);
    aiBar.className = "score-bar-fill " + getBarClass(ai.score);
    aiScore.textContent = `${ai.score}%`;
    aiScore.className = "score-value " + getScoreClass(ai.score);
    aiVerdict.textContent = ai.verdict;
    aiVerdict.className = "result-verdict " + getScoreClass(ai.score);
    aiConfidence.textContent = `Confidence: ${ai.confidence}`;
    aiDetails.textContent = ai.details;

    // --- Metrics ---
    if (ai.metrics) {
        renderMetrics(ai.metrics);
    }
}

function getScoreClass(score) {
    if (score >= 70) return "score-high";
    if (score >= 40) return "score-medium";
    return "score-low";
}

function getBarClass(score) {
    if (score >= 70) return "bar-high";
    if (score >= 40) return "bar-medium";
    return "bar-low";
}

function updateRingColor(score) {
    const svg = document.querySelector(".score-ring");
    if (!svg) return;

    let color1, color2;
    if (score >= 70) {
        color1 = "#f43f5e";
        color2 = "#f97316";
    } else if (score >= 40) {
        color1 = "#f59e0b";
        color2 = "#f97316";
    } else {
        color1 = "#10b981";
        color2 = "#06b6d4";
    }

    // Update gradient
    const grad = svg.querySelector("#ringGrad");
    if (grad) {
        grad.children[0].setAttribute("stop-color", color1);
        grad.children[1].setAttribute("stop-color", color2);
    }
}

function animateCounter(element, target) {
    let current = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const interval = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(interval);
        }
        element.textContent = current;
    }, 25);
}

function renderMetrics(metrics) {
    const metricLabels = {
        sentence_uniformity: "Sentence Uniformity",
        vocabulary_richness: "Vocabulary Richness",
        ai_phrase_density: "AI Phrase Density",
        transition_density: "Transition Density",
        burstiness: "Burstiness",
        punctuation_variety: "Punctuation Variety",
        paragraph_structure: "Paragraph Structure",
        repetition_patterns: "Repetition Patterns",
    };

    metricsGrid.innerHTML = "";

    for (const [key, value] of Object.entries(metrics)) {
        const label = metricLabels[key] || key;
        const div = document.createElement("div");
        div.className = "metric-item";
        div.innerHTML = `
            <div class="metric-name">${label}</div>
            <div class="metric-bar-track">
                <div class="metric-bar-fill ${getBarClass(value)}" style="width: 0%"></div>
            </div>
            <div class="metric-value ${getScoreClass(value)}">${value.toFixed(1)}%</div>
        `;
        metricsGrid.appendChild(div);

        // Animate after append
        setTimeout(() => {
            div.querySelector(".metric-bar-fill").style.width = `${value}%`;
        }, 400);
    }
}

// --- Toggle Metrics ---
toggleMetrics.addEventListener("click", () => {
    metricsGrid.classList.toggle("hidden");
    toggleMetrics.classList.toggle("open");
    toggleMetrics.querySelector("span").textContent = metricsGrid.classList.contains("hidden")
        ? "Show Details"
        : "Hide Details";
});

// Also toggle when clicking the header
document.querySelector("#metrics-card .result-header").addEventListener("click", (e) => {
    if (e.target !== toggleMetrics && !toggleMetrics.contains(e.target)) {
        toggleMetrics.click();
    }
});

// --- Navbar Scroll Effect ---
window.addEventListener("scroll", () => {
    const navbar = document.getElementById("navbar");
    if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }
});

// --- Hero Stats Counter Animation ---
function animateStats() {
    document.querySelectorAll(".stat-number").forEach((el) => {
        const target = parseInt(el.dataset.count);
        const suffix = el.dataset.suffix || "";
        let current = 0;
        const step = Math.max(1, Math.floor(target / 30));
        const interval = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(interval);
            }
            el.textContent = current + suffix;
        }, 40);
    });
}

// --- Intersection Observer for Animations ---
const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("animate-in");
            }
        });
    },
    { threshold: 0.1 }
);

document.querySelectorAll(".step-card, .about-content, .about-visual").forEach((el) => {
    observer.observe(el);
});

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
    injectSVGDefs();
    animateStats();
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
});
