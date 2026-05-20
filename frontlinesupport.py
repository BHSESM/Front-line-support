import streamlit as st
import pandas as pd
import requests

# --- 1. UI CONFIGURATION & PROFESSIONAL LIGHT-THEMED STYLING ---
st.set_page_config(
    page_title="Corporate Knowledge Base Engine",
    layout="wide",  
    initial_sidebar_state="collapsed"
)

# Deep clean corporate aesthetic injection with fixed background layering
st.markdown("""
    <style>
    /* Force background rendering on Streamlit's structural layout container */
    div[data-testid="stAppViewContainer"] {
        background-image: url('https://github.com/BHSESM/Front-line-support/blob/e644eeaabc18d34618a112de07811c490eb69a24/BGsearch.jpg?raw=true');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    
    /* Clear out main block background to let the underlying texture shine through */
    div[data-testid="stMainBlockContainer"] {
        background-color: transparent;
    }
    
    /* High-contrast crisp cards for search results */
    .solution-card {
        background: rgba(255, 255, 255, 0.98);
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* Strong corporate typography for high visibility */
    h1, h2, h3, h4, h5, h6, p, span, label, li {
        color: #111111 !important;
        font-weight: 500;
    }
    
    /* Bold styling for titles */
    h1, h2, h3 {
        font-weight: 700 !important;
    }
    
    /* Subdued utility labels */
    .stMarkdown caption, .stMarkdown small {
        color: #555555 !important;
    }
    
    /* Ensure text input stands out clearly against the background */
    div[data-testid="stTextInput"] {
        background: rgba(255, 255, 255, 0.9);
        padding: 10px;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    div[data-testid="stTextInput"] label {
        font-weight: bold !important;
        font-size: 1.05rem !important;
        color: #111111 !important;
    }

    /* Structured Corporate Table Elements CSS */
    div[data-testid="stTable"] table {
        width: 100% !important;
        color: #111111 !important;
        border-collapse: collapse;
    }
    div[data-testid="stTable"] th {
        background-color: #f1f3f5 !important;
        color: #111111 !important;
        text-align: left !important;
        font-weight: bold !important;
        font-size: 0.85rem !important;
        border-bottom: 2px solid #cccccc !important;
        padding: 10px !important;
    }
    div[data-testid="stTable"] td {
        color: #111111 !important;
        background-color: #ffffff !important;
        font-size: 0.85rem !important;
        border-bottom: 1px solid #e6e6e6 !important;
        padding: 10px !important;
    }
    
    /* Container to cleanly bound the corporate logo scale */
    .logo-container {
        text-align: right;
    }
    .logo-container img {
        max-width: 160px;
        height: auto;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LIVE GITHUB REPOSITORY FETCH LAYER ---
@st.cache_data(ttl=300)  # Dynamic 5-minute data stream refresh interval
def fetch_live_github_database():
    RAW_GITHUB_URL = "https://raw.githubusercontent.com/BHSESM/Front-line-support/refs/heads/main/knowledge_base.txt"
    
    try:
        response = requests.get(RAW_GITHUB_URL)
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"Failed to fetch database from GitHub. Status Code: {response.status_code}")
            return ""
    except Exception as e:
        st.error(f"Connection error to data repository: {str(e)}")
        return ""

# --- 3. DYNAMIC PARSER CORE ENGINE ---
def compile_live_runbooks(raw_text_data):
    if not raw_text_data.strip():
        return []
        
    articles = []
    current_article = None
    stop_words = {"the", "and", "a", "of", "to", "in", "is", "for", "on", "with", "as", "by", "at", "an", "this", "that", "from"}
    
    lines = raw_text_data.strip().split("\n")
    
    for raw_line in lines:
        line_str = raw_line.strip()
        
        if not line_str:
            if current_article and current_article["lines"]:
                current_article["lines"].append("")
            continue
            
        if line_str.startswith("#"):
            if current_article:
                current_article["body_text"] = "\n".join(current_article["lines"])
                articles.append(current_article)
            
            title = line_str.lstrip("# ").strip()
            
            clean_title = title.lower()
            for char in [".", ",", "-", "/", "(", ")", "!", "?", ":", ";"]:
                clean_title = clean_title.replace(char, " ")
            clean_title_words = clean_title.split()
            
            auto_tags = [w for w in clean_title_words if w not in stop_words and len(w) > 1]
            
            current_article = {
                "id": f"KB-REF-{len(articles) + 1:03d}",
                "title": title,
                "tags": auto_tags,
                "lines": []
            }
        else:
            if current_article:
                current_article["lines"].append(line_str)
                
                clean_content = line_str.lower()
                for char in [".", ",", "-", "/", "(", ")", "!", "?", ":", ";", "|"]:
                    clean_content = clean_content.replace(char, " ")
                clean_content_words = clean_content.split()
                
                for w in clean_content_words:
                    if w not in stop_words and len(w) > 2 and w not in current_article["tags"]:
                        current_article["tags"].append(w)
                        
    if current_article:
        current_article["body_text"] = "\n".join(current_article["lines"])
        articles.append(current_article)
        
    return articles

# Pull data assets into runtime space
RAW_DATA = fetch_live_github_database()
KNOWLEDGE_BASE = compile_live_runbooks(RAW_DATA)

# --- 4. ADVANCED SCORING SEARCH RUNTIME (MULTI-MATCH ENGINE) ---
def search_knowledge_base_multi(query_string):
    if not query_string.strip() or not KNOWLEDGE_BASE:
        return []
        
    cleaned_query = query_string.lower()
    for char in [".", ",", "-", "/", "(", ")", "!", "?", ":", ";"]:
        cleaned_query = cleaned_query.replace(char, " ")
    query_words = cleaned_query.split()
    
    matched_results = []
    
    for article in KNOWLEDGE_BASE:
        score = 0
        title_clean = article["title"].lower()
        body_clean = article["body_text"].lower()
        
        for word in query_words:
            if word in title_clean:
                score += 5
            if word in article["tags"]:
                score += 3
            if word in body_clean:
                score += 1
                
        if score >= 1:
            matched_results.append((article, score))
            
    matched_results.sort(key=lambda x: x[1], reverse=True)
    return matched_results

# --- 5. INTERFACE HUB DISPLAY (BUSINESS LEVEL HEADER) ---
head_col1, head_col2 = st.columns([5, 1])

with head_col1:
    st.title("Sureserve Group Knowledge Base Engine")
    st.markdown("**Centralized Cross-Departmental Resolution Portal** | Accessible by Service Desk, Dispatch, and Senior Leadership Teams.")

with head_col2:
    # Logo deployment with custom HTML styling layout overrides
    logo_url = "https://github.com/BHSESM/Front-line-support/blob/3af0eb8ca9ffdfae402502efad9f92e03dfd6944/Sureserve2.jpg?raw=true"
    st.markdown(f"""
        <div class="logo-container">
            <img src="{logo_url}">
        </div>
    """, unsafe_allow_html=True)

st.divider()

if not KNOWLEDGE_BASE:
    st.warning("🔄 System initializing or synchronizing data frames with GitHub master source ledger...")
else:
    engineer_query = st.text_input(
        "Search Knowledge Base:", 
        placeholder="Enter search queries or criteria (e.g., Job types, SX1, flashing green light, ALCS, E62...)"
    )

    if engineer_query:
        results = search_knowledge_base_multi(engineer_query)
        
        if results:
            st.write(f"### Found {len(results)} matching resolution records:")
            
            for match, match_score in results:
                st.markdown('<div class="solution-card">', unsafe_allow_html=True)
                st.subheader(f"📖 {match['title']}")
                st.caption(f"Relevance Index: {match_score} | Document Ref ID: {match['id']}")
                st.divider()
                
                # Render logic checking for multi-column data structures within strings
                if "\t" in match["body_text"] or "    " in match["body_text"] or "|" in match["body_text"]:
                    try:
                        lines = [l.strip() for l in match["body_text"].split("\n") if l.strip()]
                        table_matrix = []
                        
                        for l in lines:
                            if "\t" in l:
                                row_cells = [cell.strip() for cell in l.split("\t") if cell.strip() != ""]
                            elif "    " in l:
                                row_cells = [cell.strip() for cell in l.split("    ") if cell.strip() != ""]
                            else:
                                row_cells = [cell.strip() for cell in l.split("|") if cell.strip() != ""]
                            
                            if row_cells:
                                table_matrix.append(row_cells)
                        
                        if table_matrix and len(table_matrix) > 1:
                            headers = table_matrix[0]
                            rows = table_matrix[1:]
                            
                            max_cols = len(headers)
                            normalized_rows = []
                            for r in rows:
                                if len(r) < max_cols:
                                    r = r + [""] * (max_cols - len(r))
                                elif len(r) > max_cols:
                                    r = r[:max_cols]
                                normalized_rows.append(r)
                                
                            formatted_df = pd.DataFrame(normalized_rows, columns=headers)
                            st.table(formatted_df)
                        else:
                            st.markdown(match["body_text"])
                    except Exception:
                        st.markdown(match["body_text"])
                else:
                    st.markdown(match["body_text"])
                    
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ No exact resolution paths found for the entered keywords.")
            st.markdown("""
                <div style="background: rgba(231, 76, 60, 0.08); padding: 15px; border-radius: 6px; border: 1px solid #e74c3c; color: #c0392b;">
                    <strong>Notice:</strong> The query entered did not match existing knowledge articles.<br> 
                    Please coordinate across systems or raise a standardized tracking query with management.
                </div>
            """, unsafe_allow_html=True)

st.divider()
st.caption("Sureserve Group Knowledge Management Hub v2.0 — Production Build Consolidation")
