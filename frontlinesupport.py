import streamlit as st
import pandas as pd
import requests

# --- 1. UI CONFIGURATION & SIGNATURE CORPORATE LIGHT-THEMED STYLING ---
st.set_page_config(
    page_title="Corporate Knowledge Base Engine",
    layout="wide",  
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Direct injection to target Streamlit base layouts over the custom texture */
    div[data-testid="stAppViewContainer"] {
        background-image: url('https://github.com/BHSESM/Front-line-support/blob/e644eeaabc18d34618a112de07811c490eb69a24/BGsearch.jpg?raw=true');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    div[data-testid="stMainBlockContainer"] {
        background-color: transparent;
    }
    
    /* Clean, defined corporate white card for crisp content separation */
    .solution-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 24px;
        margin-top: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Global corporate typography overrides */
    h1, h2, h3, h4, h5, h6, p, span, label, li {
        color: #1a202c !important;
    }
    h1, h2, h3 {
        font-weight: 700 !important;
    }
    p, li {
        font-weight: 400 !important;
        line-height: 1.6;
    }
    
    /* Formatting link buttons to look professional */
    .solution-card a {
        color: #2b6cb0 !important;
        text-decoration: underline !important;
        font-weight: 600 !important;
    }
    .solution-card a:hover {
        color: #1a433e !important;
    }
    
    /* Input hub layout clarity */
    div[data-testid="stTextInput"] {
        background: rgba(255, 255, 255, 0.95);
        padding: 12px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stTextInput"] label {
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        color: #2d3748 !important;
    }

    /* Standard Data Tables Styles overrides */
    div[data-testid="stTable"] table {
        width: 100% !important;
        color: #1a202c !important;
        border-collapse: collapse;
        margin-top: 10px;
    }
    div[data-testid="stTable"] th {
        background-color: #f7fafc !important;
        color: #2d3748 !important;
        text-align: left !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        border-bottom: 2px solid #e2e8f0 !important;
        padding: 12px !important;
    }
    div[data-testid="stTable"] td {
        color: #4a5568 !important;
        background-color: #ffffff !important;
        font-size: 0.85rem !important;
        border-bottom: 1px solid #edf2f7 !important;
        padding: 12px !important;
    }
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
@st.cache_data(ttl=300)
def fetch_live_github_database():
    RAW_GITHUB_URL = "https://raw.githubusercontent.com/BHSESM/Front-line-support/refs/heads/main/knowledge_base.md"
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

RAW_DATA = fetch_live_github_database()
KNOWLEDGE_BASE = compile_live_runbooks(RAW_DATA)

# --- 4. ADVANCED SCORING SEARCH RUNTIME ---
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

# --- 5. INTERFACE HUB DISPLAY ---
head_col1, head_col2 = st.columns([5, 1])

with head_col1:
    st.title("Sureserve Group Knowledge Base Engine")
    st.markdown("**Centralized Cross-Departmental Resolution Portal** | Managed seamlessly by Service Desk, Dispatch, and SLT frameworks.")

with head_col2:
    logo_url = "https://github.com/BHSESM/Front-line-support/blob/3af0eb8ca9ffdfae402502efad9f92e03dfd6944/Sureserve2.jpg?raw=true"
    st.markdown(f'<div class="logo-container"><img src="{logo_url}"></div>', unsafe_allow_html=True)

st.divider()

if not KNOWLEDGE_BASE:
    st.warning("🔄 Connecting to live cross-departmental documentation files...")
else:
    engineer_query = st.text_input(
        "Search Knowledge Base:", 
        placeholder="Enter criteria or keywords (e.g., 3PH, Job types, SX1, ALCS, E62...)"
    )

    if engineer_query:
        results = search_knowledge_base_multi(engineer_query)
        
        if results:
            st.write(f"### Found {len(results)} matching resolution records:")
            
            for match, match_score in results:
                # Wrap everything safely inside the unified crisp white card boundaries
                st.markdown('<div class="solution-card">', unsafe_allow_html=True)
                st.subheader(f"📘 {match['title']}")
                st.caption(f"Relevance Index Score: {match_score} | Document Ref ID: {match['id']}")
                st.divider()
                
                # Check explicitly if a formal data grid matrix structure exists in prose before calling st.table
                if "|" in match["body_text"] and "\n" in match["body_text"]:
                    try:
                        lines = [l.strip() for l in match["body_text"].split("\n") if l.strip()]
                        table_matrix = []
                        
                        for l in lines:
                            if "|" in l:
                                row_cells = [cell.strip() for cell in l.split("|") if cell.strip() != ""]
                                if row_cells and not all(c == '-' for c in row_cells[0]):
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
                            st.markdown(match["body_text"], unsafe_allow_html=True)
                    except Exception:
                        st.markdown(match["body_text"], unsafe_allow_html=True)
                else:
                    # Clean prose output directly rendering structural anchors and media links
                    st.markdown(match["body_text"], unsafe_allow_html=True)
                    
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ No matching internal records located inside current documentation database.")
