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
