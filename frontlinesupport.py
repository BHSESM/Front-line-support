import streamlit as st
import pandas as pd
import os
import re

# --- 1. UI CONFIGURATION & HIGH-CONTRAST STYLING ---
st.set_page_config(
    page_title="Service Desk Knowledge Base Engine",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
    h1, h2, h3, h4, h5, h6, p, span, label, li {
        color: #ffffff !important;
    }
    div[data-testid="stTable"] table {
        width: 100% !important;
        color: #ffffff !important;
    }
    div[data-testid="stTable"] th {
        background-color: rgba(0, 255, 204, 0.15) !important;
        color: #00ffcc !important;
        text-align: left !important;
        font-weight: bold !important;
    }
    div[data-testid="stTable"] td {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTOMATED PLAIN TEXT PARSER & AUTO-TAGGER ---
@st.cache_data
def load_and_parse_text_kb():
    filename = "knowledge_base.txt"
    if not os.path.exists(filename):
        st.error("Missing infrastructure file: 'knowledge_base.txt' not found in repository root.")
        return []
        
    articles = []
    current_article = None
    
    # Simple common words to filter out of automatic tag generation
    stop_words = {"the", "and", "a", "of", "to", "in", "is", "for", "on", "with", "as", "by", "at", "an", "this", "that", "from"}
    
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                if current_article and current_article["lines"]:
                    current_article["lines"].append("")
                continue
                
            # Updated: A line starting with a hash (#) indicates a new title block
            if line_str.startswith("#"):
                if current_article:
                    current_article["body_text"] = "\n".join(current_article["lines"])
                    articles.append(current_article)
                
                title = line_str.lstrip("# ").strip()
                
                # Auto-generate search tags from the title text words directly
                clean_words = re.sub(r'[^\w\s]', '', title.lower()).split()
                auto_tags = [w for w in clean_words if w not in stop_words and len(w) > 1]
                
                current_article = {
                    "id": f"TXT-KB-{len(articles) + 1:03d}",
                    "title": title,
                    "tags": auto_tags,
                    "lines": []
                }
            else:
                if current_article:
                    current_article["lines"].append(line_str)
                    # Supplement baseline tags dynamically using content fragments
                    clean_words = re.sub(r'[^\w\s]', '', line_str.lower()).split()
                    for w in clean_words:
                        if w not in stop_words and len(w) > 3 and w not in current_article["tags"]:
                            current_article["tags"].append(w)
                            
        # Append the final item remaining in buffer
        if current_article:
            current_article["body_text"] = "\n".join(current_article["lines"])
            articles.append(current_article)
            
    return articles

KNOWLEDGE_BASE = load_and_parse_text_kb()

# --- 3. SEARCH RUNTIME MATCHING LOGIC ---
def search_knowledge_base(query_string):
    if not query_string.strip() or not KNOWLEDGE_BASE:
        return None, 0
        
    cleaned_query = re.sub(r'[^\w\s]', '', query_string.lower())
    query_words = cleaned_query.split()
    
    best_match = None
    highest_score = 0
    
    for article in KNOWLEDGE_BASE:
        score = 0
        title_clean = re.sub(r'[^\w\s]', '', article["title"].lower())
        
        for word in query_words:
            if word in title_clean:
                score += 4  # Weight heavily for direct title matches
            elif word in article["tags"]:
                score += 2  # Match background tags
                
        if score > highest_score:
            highest_score = score
            best_match = article
            
    return best_match, highest_score

# --- 4. STREAMLIT DISPLAY INTERFACE HUB ---
st.title("🤖 Service Desk Resolution Shield")
st.write("Instant verification runbook node. Auto-parsing text pipeline active.")

engineer_query = st.text_input(
    "Describe the issue or enter keywords:", 
    placeholder="e.g., Wrong job type raised, flashing red light..."
)

if engineer_query:
    match, match_score = search_knowledge_base(engineer_query)
    
    if match and match_score >= 3:
        st.markdown('<div class="solution-card">', unsafe_allow_html=True)
        st.subheader(f"✅ Best Match Found: {match['title']}")
        st.caption(f"System Confidence Index Score: {match_score} | Ref ID: {match['id']}")
        st.divider()
        
        # Look for pipeline character formatting indicating data rows
        if "|" in match["body_text"] and ("\n" in match["body_text"] or len(match["body_text"]) > 10):
            try:
                lines = [l.strip() for l in match["body_text"].split("\n") if l.strip()]
                table_matrix = []
                for l in lines:
                    table_matrix.append([cell.strip() for cell in l.split("|")])
                    
                if table_matrix:
                    headers = table_matrix[0]
                    rows = table_matrix[1:]
                    formatted_df = pd.DataFrame(rows, columns=headers)
                    st.table(formatted_df)
            except Exception:
                st.markdown(match["body_text"])
        else:
            st.markdown(match["body_text"])
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ No matching resolution path located inside local database frames.")
        st.markdown("""
            <div style="background: rgba(255, 75, 75, 0.1); padding: 15px; border-radius: 8px; border: 1px dashed #ff4b4b; color: #ffffff;">
                <strong style="color: #ff4b4b;">Procedural Action Required:</strong> The current scenario doesn't match an automated script.<br> 
                Please raise a manual <strong>Tier 2 Service Desk Escalation Request</strong> via the primary workspace hub.
            </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("Shinra ITSM Shield Layer v1.2 — 100% Verified Local Runbook Registry")
