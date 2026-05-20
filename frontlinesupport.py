import streamlit as st
import pandas as pd
import requests
import urllib.parse

# --- 1. UI CONFIGURATION & PROFESSIONAL CORPORATE STYLING ---
st.set_page_config(
    page_title="Corporate Knowledge Base Engine",
    layout="wide",  
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    div[data-testid="stAppViewContainer"] {
        background-image: url('https://github.com/BHSESM/Front-line-support/blob/e644eeaabc18d34618a112de07811c490eb69a24/BGsearch.jpg?raw=true');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    div[data-testid="stMainBlockContainer"] {
        background-color: transparent;
    }
    .solution-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 24px;
        margin-top: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3, h4, h5, h6, p, span, label, li {
        color: #1a202c !important;
    }
    div[data-testid="stTextInput"] {
        background: rgba(255, 255, 255, 0.95);
        padding: 12px;
        border-radius: 6px;
    }
    .logo-container {
        text-align: right;
    }
    .logo-container img {
        max-width: 160px;
        height: auto;
    }
    /* Meta tags badge design styling */
    .file-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .badge-pdf { background-color: #fee2e2; color: #991b1b; }
    .badge-image { background-color: #fef3c7; color: #92400e; }
    .badge-ppt { background-color: #e0f2fe; color: #075985; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTOMATED DIRECTORY SCANNING HUB ---
GITHUB_USER = "BHSESM"
GITHUB_REPO = "Front-line-support"

@st.cache_data(ttl=60)  # Checked folders refresh every 60 seconds
def scan_github_folders():
    """Scans repository directories using public API frameworks to index live assets"""
    categories = {
        "pdfs": "📄 PDF Document",
        "images": "🖼️ Visual Reference / Image",
        "powerpoints": "📊 PowerPoint Presentation"
    }
    indexed_files = []
    
    for folder_name, display_type in categories.items():
        # Hit public repository folder schema
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{folder_name}"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                files_list = response.json()
                for file_obj in files_list:
                    # Isolate standard files vs folders
                    if file_obj["type"] == "file":
                        filename = file_obj["name"]
                        
                        # Generate clean human-readable title by pulling off trailing extension format
                        clean_title = filename.rsplit('.', 1)[0]
                        
                        # Fixes space mapping directly for raw content streaming loops
                        encoded_name = urllib.parse.quote(filename)
                        download_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{folder_name}/{encoded_name}"
                        
                        indexed_files.append({
                            "title": clean_title,
                            "filename": filename,
                            "type": display_type,
                            "folder": folder_name,
                            "url": download_url
                        })
        except:
            pass  # Fail gracefully if a specific folder hasn't been created yet
            
    return indexed_files

# Compile database from raw directory listings
LIVE_ASSET_DATABASE = scan_github_folders()

# --- 3. DYNAMIC ASSET SEARCH CORE ---
def search_assets(query_string):
    if not query_string.strip() or not LIVE_ASSET_DATABASE:
        return []
        
    query_words = query_string.lower().split()
    matched_results = []
    
    for asset in LIVE_ASSET_DATABASE:
        score = 0
        title_lower = asset["title"].lower()
        
        # Priority mapping score index based on keywords match weight counts
        for word in query_words:
            if word in title_lower:
                score += 10
                
        if score > 0:
            matched_results.append(asset)
            
    return matched_results

# --- 4. INTERFACE HUB DISPLAY ---
head_col1, head_col2 = st.columns([5, 1])
with head_col1:
    st.title("Sureserve Group Knowledge Base Engine")
    st.markdown("**Centralized Cross-Departmental Asset Portal** | Fully Automated Zero-Maintenance Directory Service.")
with head_col2:
    logo_url = "https://github.com/BHSESM/Front-line-support/blob/3af0eb8ca9ffdfae402502efad9f92e03dfd6944/Sureserve2.jpg?raw=true"
    st.markdown(f'<div class="logo-container"><img src="{logo_url}"></div>', unsafe_allow_html=True)

st.divider()

if not LIVE_ASSET_DATABASE:
    st.info("ℹ️ Repositories directory mapping empty. Please verify file uploads exist inside `/pdfs`, `/images`, or `/powerpoints` on GitHub.")
else:
    user_query = st.text_input(
        "Search Group Documents & Assets:", 
        placeholder="Type search terms here (e.g., ECO, 3PH, Termination, Policy...)"
    )

    if user_query:
        search_matches = search_assets(user_query)
        
        if search_matches:
            st.write(f"### Located {len(search_matches)} Matching Assets:")
            
            for asset in search_matches:
                st.markdown('<div class="solution-card">', unsafe_allow_html=True)
                
                # Dynamic badge application
                badge_class = "badge-pdf" if asset["folder"] == "pdfs" else ("badge-image" if asset["folder"] == "images" else "badge-ppt")
                st.markdown(f'<span class="file-badge {badge_class}">{asset["type"]}</span>', unsafe_allow_html=True)
                
                st.subheader(asset["title"])
                st.caption(f"File System Source Target: /{asset['folder']}/{asset['filename']}")
                st.write("")
                
                # Layout logic presentation fork
                if asset["folder"] == "images":
                    # Direct layout render embedding for visual files
                    st.image(asset["url"], use_container_width=True)
                else:
                    # Standard execution tracking for documentation download streams
                    st.link_button(f"📥 Launch & View Asset: {asset['filename']}", asset["url"])
                    
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ No matching internal assets located inside directory index structures.")

st.divider()
st.caption("Sureserve Group Knowledge Management Hub v3.0 — Automated Framework Consolidation")
