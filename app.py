import streamlit as st
import pypdf
import docx
import json
import re
from openai import OpenAI
from google import genai
from google.genai import types
import traceback

# ==========================================
# 1. Page Config & State Initialization
# ==========================================
st.set_page_config(
    page_title="慧聘 · 智析官 | TalentScout AI",
    page_icon="🎯",
    layout="wide"
)

# 初始化各候選人的獨立分析狀態與反饋歷史
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}  
if 'hr_feedback_history' not in st.session_state:
    st.session_state.hr_feedback_history = {} 

default_token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GEMINI_API_KEY", "")

# ==========================================
# 2. Localization Dictionaries (語系解耦)
# ==========================================
UI_ZH = {
    "sys_config": "⚙️ 系統設定",
    "key_mode": "選擇 AI 金鑰模式：",
    "default_key": "使用開源公共免費額度",
    "byok_key": "使用自備 AI API Key (無限制)",
    "loaded_default": "🌱 **開源公共資源已載入 (10次/Session)**。歡迎自由體驗！若需高頻批量篩選或處理高度機密履歷，建議切換為自備 Key 以確保最高安全性與不限次數體驗。",
    "quota_exceeded": "🤝 **本 Session 試用額度已達上限。** 請刷新網頁（F5）或切換至『使用自備 AI API Key』繼續使用！",
    "select_provider": "選擇 AI 供應商：",
    "enter_key": "輸入你的 {} Key",
    "framework_title": "🛡️ 數據安全與進階 HR 管治特色",
    "framework_body": """
    **🔐 企業隱私防護:**
    - **零數據留存:** 運算僅存於本地 Session 記憶體，重整即刻物理銷毀。
    **🎯 進階 HR Tech 引擎:**
    - **多 CV 獨立解析 (Tabbed UI):** 批量上傳，獨立分頁精準生成決策報告。
    - **深度 DEI 詞彙偵測:** 具體揪出年齡、性別等潛在偏見字眼並提供修正。
    - **決策報告一鍵匯出:** 支援將 AI 分析結果匯出為 Markdown 報告。
    """,
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)",
    "subtitle": "🚀 **企業級 ATS 智慧初篩、勝任力評估與多元包容 (DEI) 管治系統**",
    "col1_title": "📄 1. 職位描述 (JD)",
    "input_mode_lbl": "輸入方式",
    "input_modes": ["貼上文字", "上傳文件"],
    "jd_ph": "請貼上 JD 內容，包含職責與資格等...",
    "upload_jd_lbl": "上傳 JD 檔案 (PDF, DOCX, 限 15MB 內)",
    "col2_title": "👤 2. 求職者履歷 (CV)",
    "upload_cv_lbl": "上傳 CV 檔案 (可多選，獨立生成報告)",
    "col3_title": "🎯 3. 招聘情境與設定",
    "referral_lbl": "🎖️ 此批次包含內部員工推薦",
    "urgency_lbl": "⏳ 職位招聘急迫性",
    "urgency_opts": ["標準 (Standard)", "緊急 (Urgent)"],
    "special_req_lbl": "其他特殊要求 (JD 補充)",
    "special_req_ph": "例如：必須精通廣東話、具備 ISO 審計經驗",
    "run_btn": "🚀 啟動多維度 ATS 解析與結構化評估",
    "status_analyzing": "🚀 正在獨立解析候選人：{}",
    "err_json": "❌ AI 回傳格式解析失敗。請嘗試重新執行。",
    "err_api": "❌ API 呼叫失敗或超時，請檢查連線狀態或 API Key 權限。",
    "sec1_title": "📊 1. 漏斗決策與 ATS 匹配度",
    "m_score": "綜合勝任力得分",
    "m_ats": "ATS 關鍵字匹配率",
    "m_rec": "漏斗轉換建議",
    "m_time": "到職時效評估",
    "ats_matched": "✅ 命中關鍵字:",
    "ats_missing": "❌ 缺失關鍵字:",
    "sec2_title": "📈 2. 核心勝任力維度拆解",
    "evidence_source": "證據來源",
    "sec3_title": "🛡️ 3. DEI 防偏誤審查與風險管治",
    "dei_check": "⚖️ DEI 潛在偏見詞彙與防偏誤措施:",
    "hard_risks": "🚨 絕對風險/合規死線:",
    "soft_risks": "⚠️ 軟性風險/面試觀察點:",
    "sec4_title": "🎯 4. 結構化面試量表 (STAR)",
    "sec4_sub": "💡 *基於勝任力模型生成之標準化評分題庫，確保面試官評分一致性。*",
    "probe_q": "🗣️ 面試題:",
    "rubric_5": "🟢 5分 (優秀):",
    "rubric_3": "🟡 3分 (合格):",
    "rubric_1": "🔴 1分 (需關注):",
    "sec5_title": "🤝 5. HR 漏斗覆核與動態校正 (HITL)",
    "feedback_ph": "輸入針對此候選人的初篩結果或補充觀察...",
    "re_eval_btn": "🔄 結合 HR 反饋重新校正此候選人模型",
    "download_btn": "📥 下載此候選人評估報告 (Markdown)"
}

UI_EN = {
    "sys_config": "⚙️ System Config",
    "key_mode": "Select AI Key Mode:",
    "default_key": "Use Open-Source Public Quota",
    "byok_key": "Use Custom API Key (Unlimited)",
    "loaded_default": "🌱 **Public Quota Loaded (10 uses/session).** For high-frequency or highly confidential CV processing, BYOK is strongly recommended for maximum security.",
    "quota_exceeded": "🤝 **Quota Reached!** Please refresh page or switch to 'Custom Key' to continue.",
    "select_provider": "Select AI Provider:",
    "enter_key": "Enter your {} Key",
    "framework_title": "🛡️ Privacy & AI Governance",
    "framework_body": """
    **🔐 Enterprise Privacy Guarantee:**
    - **Zero Retention:** Processed strictly in-memory per session.
    **🎯 Advanced HR Tech Engine:**
    - **Isolated Multi-CV Tabs:** Process batch uploads with independent evaluation tabs.
    - **Deep DEI Auditing:** Explicitly flags biased terminology (age, gender, origin).
    - **One-Click Export:** Download full assessment reports in Markdown.
    """,
    "title": "🎯 TalentScout AI",
    "subtitle": "🚀 **Enterprise ATS Screening, Competency Assessment & DEI Governance System**",
    "col1_title": "📄 1. Job Description (JD)",
    "input_mode_lbl": "Input Method",
    "input_modes": ["Paste Text", "Upload Files"],
    "jd_ph": "Paste JD content here including duties, requirements...",
    "upload_jd_lbl": "Upload JD Files (PDF, DOCX, Max 15MB)",
    "col2_title": "👤 2. Candidate Resumes (CV)",
    "upload_cv_lbl": "Upload CV Files (Multiple files for batch tabs)",
    "col3_title": "🎯 3. Hiring Context",
    "referral_lbl": "🎖️ Internal Referral Batch",
    "urgency_lbl": "⏳ Time-to-Fill Urgency",
    "urgency_opts": ["Standard", "Urgent"],
    "special_req_lbl": "Special Requirements (JD Add-on)",
    "special_req_ph": "E.g., Fluent Cantonese, ISO Audit experience required",
    "run_btn": "🚀 Run Full ATS & Competency Audit",
    "status_analyzing": "🚀 Independently analyzing candidate: {}",
    "err_json": "❌ JSON Parse Error. The AI output was malformed.",
    "err_api": "❌ API Connection Error. Please check your network or API Key.",
    "sec1_title": "📊 1. Funnel Verdict & ATS Match",
    "m_score": "Competency Score",
    "m_ats": "ATS Keyword Match",
    "m_rec": "Funnel Recommendation",
    "m_time": "Time-to-Fill Assessment",
    "ats_matched": "✅ Matched Keywords:",
    "ats_missing": "❌ Missing Keywords:",
    "sec2_title": "📈 2. Core Competency Breakdown",
    "evidence_source": "Evidence Source",
    "sec3_title": "🛡️ 3. DEI Safeguards & Risk Governance",
    "dei_check": "⚖️ DEI Biased Keywords Flagged & Mitigation:",
    "hard_risks": "🚨 Hard Risks / Compliance Blocks:",
    "soft_risks": "⚠️ Soft Risks / Interview Focus:",
    "sec4_title": "🎯 4. Structured Interview Rubric (STAR)",
    "sec4_sub": "💡 *Standardized scoring rubrics generated based on competency models for consistency.*",
    "probe_q": "🗣️ Question:",
    "rubric_5": "🟢 5 pts (Excellent):",
    "rubric_3": "🟡 3 pts (Acceptable):",
    "rubric_1": "🔴 1 pt (Poor):",
    "sec5_title": "🤝 5. Human-in-the-Loop Re-eval",
    "feedback_ph": "Enter HR screening notes for this specific candidate...",
    "re_eval_btn": "🔄 Update Evaluation for this Candidate",
    "download_btn": "📥 Download Assessment Report (Markdown)"
}

with st.sidebar:
    output_lang = st.selectbox("🌐 界面與報告語言 (UI & Output Language):", ["繁體中文 (Traditional Chinese)", "English (Full)"], index=0)
    st.divider()

is_zh = output_lang == "繁體中文 (Traditional Chinese)"
def get_ui(key, default=""):
    return (UI_ZH if is_zh else UI_EN).get(key, default)

# ==========================================
# 3. Sidebar Config (Public Quota + BYOK)
# ==========================================
AI_PROVIDERS = {
    "OpenAI": {"url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "DeepSeek": {"url": "https://api.deepseek.com", "model": "deepseek-chat"},
    "Groq": {"url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile"},
    "Google Gemini": {"url": "N/A", "model": "gemini-2.5-flash"},
    "GitHub Models": {"url": "https://models.inference.ai.azure.com", "model": "gpt-4o-mini"}
}

with st.sidebar:
    st.header(get_ui("sys_config"))
    if default_token:
        key_mode = st.radio(get_ui("key_mode"), [get_ui("default_key"), get_ui("byok_key")], index=0)
    else:
        key_mode = get_ui("byok_key")

    if key_mode == get_ui("default_key"):
        provider = "GitHub Models"
        api_key = default_token
        st.info(get_ui("loaded_default"))
    else:
        provider = st.selectbox(get_ui("select_provider"), list(AI_PROVIDERS.keys()))
        api_key = st.text_input(get_ui("enter_key").format(provider), type="password")
    
    st.divider()
    st.markdown(get_ui("framework_title"))
    st.markdown(get_ui("framework_body"))

def check_quota():
    if key_mode == get_ui("default_key"):
        if st.session_state.usage_count >= 10:
            st.error(get_ui("quota_exceeded"))
            st.stop()
        st.session_state.usage_count += 1

# ==========================================
# 4. Core Functions & UI Helpers
# ==========================================
def extract_single_file(file):
    if not file: return ""
    text = ""
    file_type = file.name.split('.')[-1].lower()
    try:
        if file_type == "pdf":
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages: text += (page.extract_text() or "") + "\n"
        elif file_type in ["docx", "doc"]:
            doc = docx.Document(file)
            for para in doc.paragraphs: text += para.text + "\n"
    except Exception:
        pass
    return text.strip()

def extract_text_from_files(uploaded_files):
    if not uploaded_files: return ""
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]
    return "\n".join([extract_single_file(f) for f in uploaded_files])

# 新增：智能擷取分頁名稱 (去除副檔名與職稱，只保留人名)
def format_tab_name(filename):
    clean = re.sub(r'(?i)(\.pdf|\.docx|\.doc)', '', filename)
    clean = re.sub(r'(?i)(resume|cv|profile|履歷).*', '', clean).strip()
    words = clean.split()
    if len(words) > 2:
        cut_idx = len(words)
        for i, w in enumerate(words):
            if w.lower() in ['executive', 'assistant', 'manager', 'director', 'senior', 'head', 'lead']:
                cut_idx = i
                break
        if 0 < cut_idx < len(words):
            return " ".join(words[:cut_idx])
        return " ".join(words[:4]) + "..." if len(words) > 4 else clean
    return clean

def robust_json_parse(raw_text):
    try:
        match = re.search(r'```(?:json)?\s*(.*?)\s*
