from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
import os
import datetime

app = FastAPI()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

class FIRRequest(BaseModel):
    name: str
    city: str
    state: str
    incident: str

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FIR Draft Assistant</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
    background: #0a0a0a;
    color: #fff;
    min-height: 100vh;
    padding: 24px 16px;
}
.container { max-width: 680px; margin: 0 auto; }
.badge {
    display: inline-block;
    background: #ff4500;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 4px 10px;
    border-radius: 4px;
    margin-bottom: 14px;
    text-transform: uppercase;
}
h1 {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 8px;
}
.subtitle {
    color: #888;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 28px;
}
.card {
    background: #111;
    border: 1px solid #222;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 480px) { .row { grid-template-columns: 1fr; } }
.field { margin-bottom: 16px; }
label {
    display: block;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #777;
    text-transform: uppercase;
    margin-bottom: 6px;
}
input, textarea {
    width: 100%;
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    color: #fff;
    font-size: 14px;
    padding: 11px 14px;
    outline: none;
    transition: border-color 0.15s;
    font-family: inherit;
}
input:focus, textarea:focus { border-color: #ff4500; }
textarea {
    resize: vertical;
    min-height: 130px;
    line-height: 1.6;
}
input::placeholder, textarea::placeholder { color: #444; }
.btn {
    width: 100%;
    background: #ff4500;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 700;
    padding: 14px;
    cursor: pointer;
    transition: background 0.15s, opacity 0.15s;
    font-family: inherit;
    letter-spacing: 0.02em;
}
.btn:hover { background: #e03d00; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.loading {
    display: none;
    text-align: center;
    padding: 20px;
    color: #666;
    font-size: 14px;
}
.spinner {
    display: inline-block;
    width: 18px;
    height: 18px;
    border: 2px solid #333;
    border-top-color: #ff4500;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }
.output { display: none; }
.output.visible { display: block; }
.output-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.output-label {
    font-size: 11px;
    font-weight: 700;
    color: #ff4500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.copy-btn {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    color: #aaa;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    width: auto;
    font-family: inherit;
    transition: border-color 0.15s;
}
.copy-btn:hover { border-color: #555; color: #fff; }
.fir-text {
    background: #0d0d0d;
    border: 1px solid #1e1e1e;
    border-radius: 8px;
    padding: 20px;
    font-size: 13px;
    line-height: 1.9;
    color: #ccc;
    white-space: pre-wrap;
    font-family: 'Courier New', Courier, monospace;
    word-break: break-word;
}
.notice {
    margin-top: 14px;
    background: #110a00;
    border: 1px solid #3a2000;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 12px;
    color: #cc8833;
    line-height: 1.6;
}
.steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 16px;
}
@media (max-width: 480px) { .steps { grid-template-columns: 1fr; } }
.step {
    background: #111;
    border: 1px solid #222;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.step-num {
    font-size: 22px;
    font-weight: 800;
    color: #ff4500;
    margin-bottom: 6px;
}
.step-text { font-size: 12px; color: #888; line-height: 1.5; }
</style>
</head>
<body>
<div class="container">
    <div class="badge">FIR Draft Assistant</div>
    <h1>Turn your complaint into a proper FIR draft</h1>
    <p class="subtitle">Describe what happened in plain language. Get a formatted FIR you can walk into any police station with.</p>

    <div class="steps">
        <div class="step"><div class="step-num">1</div><div class="step-text">Describe the incident in plain words</div></div>
        <div class="step"><div class="step-num">2</div><div class="step-text">Get a formatted FIR with BNS sections</div></div>
        <div class="step"><div class="step-num">3</div><div class="step-text">Walk into any police station and file</div></div>
    </div>

    <div class="card" style="margin-top:16px;">
        <div class="row">
            <div class="field">
                <label>Your Full Name</label>
                <input type="text" id="name" placeholder="e.g. Rahul Sharma" />
            </div>
            <div class="field">
                <label>State</label>
                <input type="text" id="state" placeholder="e.g. Karnataka" />
            </div>
        </div>
        <div class="field">
            <label>City / Area</label>
            <input type="text" id="city" placeholder="e.g. Bengaluru, Koramangala" />
        </div>
        <div class="field">
            <label>What happened? Write in plain language</label>
            <textarea id="incident" placeholder="e.g. Someone stole my laptop bag from a café in Koramangala on 12 September 2026. I stepped away from my table for 5 minutes and when I returned the bag was gone. It contained my laptop, wallet with cards, and my ID..."></textarea>
        </div>
        <button class="btn" id="generateBtn" onclick="generate()">Generate FIR Draft</button>
    </div>

    <div class="loading" id="loading">
        <span class="spinner"></span> Drafting your FIR...
    </div>

    <div class="card output" id="output">
        <div class="output-header">
            <span class="output-label">Your FIR Draft</span>
            <button class="copy-btn" onclick="copyFIR()">Copy Text</button>
        </div>
        <div class="fir-text" id="firText"></div>
        <div class="notice">
            ⚠️ This is an AI-generated draft to help you structure your complaint. Verify the BNS/IPC sections with the duty officer or a lawyer before filing. The draft does not constitute legal advice.
        </div>
    </div>
</div>

<script>
async function generate() {
    const name = document.getElementById('name').value.trim();
    const state = document.getElementById('state').value.trim();
    const city = document.getElementById('city').value.trim();
    const incident = document.getElementById('incident').value.trim();

    if (!name || !state || !city || !incident) {
        alert('Please fill in all fields before generating.');
        return;
    }

    const btn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const output = document.getElementById('output');

    btn.disabled = true;
    btn.textContent = 'Generating...';
    loading.style.display = 'block';
    output.classList.remove('visible');

    try {
        const res = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, state, city, incident })
        });
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        document.getElementById('firText').textContent = data.fir;
        output.classList.add('visible');
        output.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (e) {
        alert('Something went wrong. Please try again.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate FIR Draft';
        loading.style.display = 'none';
    }
}

function copyFIR() {
    const text = document.getElementById('firText').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.querySelector('.copy-btn');
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = orig, 2000);
    });
}
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

@app.post("/generate")
def generate_fir(req: FIRRequest):
    today = datetime.date.today().strftime("%d %B %Y")
    prompt = f"""You are a legal aid assistant in India. Draft a formal FIR (First Information Report) complaint letter based on the details provided.

Use this exact format:

TO,
The Station House Officer,
[Nearest relevant Police Station],
{req.city}, {req.state}

SUBJECT: Complaint Regarding [Identify the crime type clearly]

Respected Sir/Madam,

I, {req.name}, a resident of {req.city}, {req.state}, wish to bring the following matter to your kind attention and request registration of FIR:

INCIDENT NARRATION:
[Write a formal 4-6 sentence narration of the incident based on what the complainant described. Use formal language. Include date, time, location, what was lost/happened.]

APPLICABLE SECTIONS (BNS 2023 / IPC):
[List 2-3 most relevant sections with their names. Prefer BNS 2023 sections where applicable.]

LOSS/DAMAGE SUFFERED:
[List what was lost or the harm suffered]

RELIEF REQUESTED:
1. Registration of FIR
2. Investigation of the matter
3. [Any other specific relief relevant to the incident]

DOCUMENTS/EVIDENCE TO CARRY TO POLICE STATION:
[List 3-5 items the person should bring: ID proof, any receipts, screenshots, etc. relevant to this specific case]

I hereby declare that the above information is true to the best of my knowledge.

Yours faithfully,
{req.name}
Date: {today}
City: {req.city}, {req.state}

---
Incident details from complainant:
Name: {req.name}
City: {req.city}
State: {req.state}
What happened: {req.incident}

Write the complete FIR draft now. Use BNS 2023 sections (Bharatiya Nyaya Sanhita) over old IPC wherever the section exists. Keep the language formal, precise, and legally appropriate. Do not add any preamble or explanation outside the FIR format itself."""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return {"fir": response.text}
