import streamlit as st
import pandas as pd

# --- 1. UI CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Service Desk Knowledge Base Engine",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling to match your Midgar-Ops framework style
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .solution-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 12px;
        padding: 25px;
        margin-top: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    h1, h2, h3, p, span, label {
        color: #f0f0f0 !important;
    }
    div[data-testid="stTable"] th {
        background-color: rgba(0, 255, 204, 0.1) !important;
        color: #00ffcc !important;
        text-align: left !important;
    }
    div[data-testid="stTable"] td {
        color: #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DETERMINISTIC HARDCODED KNOWLEDGE BASE DATA ---
# This dictionary maps directly to your 3 core documents and fallback tags
KNOWLEDGE_BASE = [
    {
        "id": "KB-001",
        "title": "ALCS Jobs Vs. Non-ALCS Jobs Raised Incorrectly",
        "tags": ["alcs", "non-alcs", "wrong job", "raised incorrectly", "terminal", "element", "3ph", "three phase", "abort", "tl", "5 terminal", "bung", "mismatch"],
        "is_table": True,
        "table_data": {
            "Job Raised": [
                "Electric Single Element (No ALCS)", 
                "Electric 3PH (No ALCS)", 
                "Electric Single Element ALCS", 
                "Electric 3PH ALCS"
            ],
            "What Property Needs": [
                "ALCS (5 Terminal) Needed", 
                "ALCS (5 Terminal) Needed", 
                "5 Terminal NOT Needed", 
                "5 Terminal NOT Needed"
            ],
            "How to Proceed": [
                "Must abort with code from TL for wrong job type raised.", 
                "Must abort with code from TL for wrong job type raised.", 
                "Fit 5T, bung the 5th. Job can still be completed.", 
                "Fit 5T, bung the 5th. Job can still be completed."
            ]
        },
        "additional_text": ""
    },
    {
        "id": "KB-002",
        "title": "Whitelisted / Installed-Not-Commissioned / Commissioned Assets",
        "tags": ["whitelist", "whitelisted", "installed", "commissioned", "hva", "han", "save", "exchange", "pre-pay", "warrant", "sx1", "smart to smart", "s2s", "inv", "investigation", "chub", "hub", "devices to remain", "hht", "mf lookup"],
        "is_table": False,
        "body_text": """
**Asset Status & Management (HVA)**
During commissioning, assets typically move through three stages on the HVA. Understanding these helps determine if an asset can be "saved" or if it needs to be exchanged.

##### 🌐 The Three Asset States:
* **Whitelisted:** The asset was included in a submission but failed to join the HAN.
* **Installed Not Commissioned:** The asset has successfully joined the HAN but has not completed the key commissioning steps.
* **Commissioned:** The asset has joined the HAN and finished all commissioning steps.

⚠️ **IMPORTANT:** Achieving "Commissioned" status is **NOT** valid grounds to leave the site early on Pre-Pay (PP) Warrant work.

##### 📋 Job-Specific Logic (SX1 & INV):
* **SX1 Work (Smart to Smart / S2S)**
  If the asset appears on the HVA (regardless of its status), you must attempt the job as Smart to Smart (S2S) first. Only send the job as Dumb to Smart if the system presents an explicit error.
* **INV Work (Investigation)**
  Before working on any other assets, CHUB communication must be confirmed. If the Hub isn't talking, do not attempt commissioning or exchanges.

##### 🛠️ The "Devices to Remain" Logic (For Whitelisted or Installed Not Commissioned assets):
1. Add the assets to the **"Devices to Remain"** worksheet.
2. Do not complete the confirmations yet; attempt a **HHT submission** first.
3. The system will perform an MF lookup. If valid, it will either:
   * Open the HAN to allow the engineer to join the device.
   * Automatically move the asset to Commissioned without engineer interaction.
4. If this logic fails, then a physical exchange can be considered.
        """
    },
    {
        "id": "KB-003",
        "title": "LED Sequences for Communication Hubs (HAN & WAN Guide)",
        "tags": ["led", "sequence", "hub", "flashing", "frequency", "hff", "mff", "lff", "han", "wan", "red", "green", "solid", "no light", "power off", "signal", "reboot", "pairing", "disconnect"],
        "is_table": False,
        "body_text": """
##### 📊 Frequency Matrix
* **High Frequency (HFF):** 0.1s ON / 0.5s OFF ──> *Error: Action required*
* **Medium Frequency (MFF):** 0.1s ON / 2.0s OFF ──> *Transition: System is updating/changing*
* **Low Frequency (LFF):** 0.1s ON / 5.0s OFF ──> *Normal: System is running correctly*

##### 📶 HAN (Home Area Network) Status Guide
* 🔴 **No Light:** Power Off / Hub not working. Check power. If on, replace Hub.
* 🔴 **Flashing RED (Medium):** Starting Up (Normal). Max 60 secs. Wait, reset if longer.
* 🔴 **Solid RED:** Device Joined (Success!). Lasts 5 seconds. Nothing required.
* 🔴 **Flashing RED (High):** Join Failed (Error). Lasts 5 seconds. Retry pairing log.
* 🟢 **Solid GREEN:** Ready but no devices found. Follow steps to pair smart devices.
* 🟢 **Flashing GREEN (Medium):** Pairing Mode (Normal). Up to 60 mins. Start pairing on device now.
* 🟢 **Flashing GREEN (Low):** All Good (Normal). Final State. No action needed.
* 🟢 **Flashing GREEN (High):** System Error. Max 5 secs. Wait for auto-reboot or manual reset.

##### 🌐 WAN (Wide Area Network) Status Guide
* 🟢 **Flashing GREEN (Medium):** Connecting... Up to 5 mins. Wait for connection or low coverage check.
* 🟢 **Flashing GREEN (Low):** Connected (Normal). Permanent state. No action needed.
* 🟢 **Flashing GREEN (Medium):** Disconnected (Signal Lost). Hub trying to reconnect. Update Incident Record if stagnant.
* 🟢 **Flashing GREEN (High):** Network Error. Max 5 secs. Auto-reboot or replace Hub if stuck.
        """
    }
]

# --- 3. SEARCH PROCESSING ENGINE ---
def search_knowledge_base(query_string):
    if not query_string.strip():
        return None, 0
    
    # Standardize input string data matrix strings down
    cleaned_query = re.sub(r'[^\w\s]', '', query_string.lower())
    query_words = cleaned_query.split()
    
    best_match = None
    highest_score = 0
    
    for article in KNOWLEDGE_BASE:
        score = 0
        # Check intersections inside Title
        title_clean = re.sub(r'[^\w\s]', '', article["title"].lower())
        for word in query_words:
            if word in title_clean:
                score += 3  # High value for structural title keyword matches
            if word in article["tags"]:
                score += 2  # Standard tag points fallback values
                
        if score > highest_score:
            highest_score = score
            best_match = article
            
    return best_match, highest_score

# --- 4. THE LIVE FRONT END ---
st.title("🤖 Service Desk Resolution Shield")
st.write("Instant verification runbook node. Search by error codes, light patterns, or asset types.")

engineer_query = st.text_input(
    "Describe the issue or enter keywords:", 
    placeholder="e.g., Wrong job type raised, flashing red light, asset whitelisted..."
)

if engineer_query:
    # We require a threshold score of at least 2 to display results confidently
    match, match_score = search_knowledge_base(engineer_query)
    
    if match and match_score >= 2:
        st.markdown(f'<div class="solution-card">', unsafe_allow_html=True)
        st.subheader(f"✅ Best Match Found: {match['title']}")
        st.caption(f"System Confidence Index Score: {match_score} | Document Ref: {match['id']}")
        st.divider()
        
        # Format the display engine depending on content type
        if match["is_table"]:
            st.table(pd.DataFrame(match["table_data"]))
            if match["additional_text"]:
                st.write(match["additional_text"])
        else:
            st.markdown(match["body_text"])
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Fallback Escalate Block
        st.error("❌ No matching resolution path located inside local database frames.")
        st.markdown(f"""
            <div style="background: rgba(255, 75, 75, 0.1); padding: 15px; border-radius: 8px; border: 1px dashed #ff4b4b;">
                <strong>Procedural Action Required:</strong> The current scenario doesn't match an automated script.<br> 
                Please raise a manual <strong>Tier 2 Service Desk Escalation Request</strong> via the primary workspace hub.
            </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("Shinra ITSM Shield Layer v1.0 — 100% Verified Local Runbook Registry")
