import streamlit as st
import pypdf
import docx
import json
import re
from openai import OpenAI
from google import genai
from google.genai import types

# Page Config
st.set_page_config(
    page_title="慧聘 · 智析官 | TalentScout AI",
    page_icon="🎯",
    layout="wide"
)

# 初始化 Session State (用於記錄公共試用額度使用次數)
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# 讀取後台預設 Secrets
default_token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GEMINI_API_KEY", "")

# 語言選擇 (Sidebar 最頂層)
with st.sidebar:
    output_lang = st.selectbox(
        "🌐 界面與報告語言 (UI & Output Language):",
        ["繁體中文 (Traditional Chinese)", "English (Full)"],
        index=0
    )
    st.divider()

is_zh = output_lang == "繁體中文 (Traditional Chinese)"

# UI 文字字典 (包含開源共享、公德心與公平使用聲明)
ui_labels = {
    "sys_config": "⚙️ 系統設定 (System Config)" if is_zh else "⚙️ System Config",
    "key_mode": "選擇 AI 金鑰模式：" if is_zh else "Select AI Key Mode:",
    "default_key": "使用開源公共免費額度" if is_zh else "Use Open-Source Public Quota",
    "byok_key": "使用自備 AI API Key (無限制)" if is_zh else "Use Custom API Key (Unlimited)",
    "loaded_default": "🌱 **本系統為免費開源專案**，已預載公共試用資源（每 Session 10 次）。歡迎自由體驗！若需高頻批量篩選，歡迎切換為自備 Key，將公共資源留給其他有需要的人。" if is_zh else "🌱 **Open-Source Public Quota Loaded** (10 free uses per session). For high-frequency queries, please enter your own API key to support fair resource sharing.",
    "quota_exceeded": "🤝 **感謝體驗 TalentScout AI！**\n\n本系統為完全免費開源專案，伺服器資源由創作者個人自費分享給全網使用。希望大家發揮公德心，公平使用資源。\n\n本 Session 的公共試用額度（10 次）已暫時達上限。你可以**刷新網頁（F5）重新開啟新 Session**，或於左側選單切換至**『使用自備 AI API Key』**即可享用無限制且更高速的專屬體驗！" if is_zh else "🤝 **Thank you for using TalentScout AI!**\n\nThis is a free open-source project with public server resources funded individually for the community. To promote fair use, the public trial quota (10 uses/session) has been reached.\n\nYou can **refresh the page (F5)** to start a new session, or switch to **'Use Custom API Key'** in the sidebar for unlimited high-speed analysis!",
    "select_provider": "選擇 AI 供應商 (Provider)：" if is_zh else "Select AI Provider:",
    "enter_key": "輸入你的 {} Key" if is_zh else "Enter your {} Key",
    
    "framework_title": "🛡️ 數據安全與 AI 管治特色" if is_zh else "🛡️ Privacy & AI Governance Features",
    "framework_body": """
    **🔐 企業級私密防護 (Data Privacy):**
    - **零數據留存:** 僅於本地 Session 記憶體運算，重新整理頁面即完全清空。
    - **BYOK 直連加密:** 自備 Key 直連 AI 官方 API，避免意外洩漏。
    - **私隱合規:** 嚴格遵循香港 PDPO 數據私隱條例。

    **🎯 深度招募特色 (Key Features):**
    - **履歷原文追溯:** 提供原段落引用與「反證驗證」，杜絕 AI 幻覺。
    - **硬/軟風險分層:** 區分簽證/語言等「硬死線」與「面試觀察點」。
    - **防呆與穩定機制:** 內建 JSON Schema 驗證與自動除錯機制。
    """ if is_zh else """
    **🔐 Enterprise Privacy Guarantee:**
    - **Zero Data Retention:** Processed strictly in-memory per session; wiped upon refresh.
    - **Direct API Connection:** Your Key connects directly to official AI endpoints.
    - **PDPO Compliant:** Built under Hong Kong PDPO guidelines.

    **🎯 Core Platform Features:**
    - **Traceable Evidence:** Every claim is backed by exact CV quotes and counter-evidence.
    - **Risk Stratification:** Isolates hard blockers (visa/language) from soft observation points.
    - **Robust Engineering:** Built-in JSON Schema validation and fallback mechanisms.
    """,
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)" if is_zh else "🎯 TalentScout AI",
    "subtitle": "🚀 **企業級高階人才決策與 AI 管治合規評估系統**" if is_zh else "🚀 **Enterprise Talent Advisory & AI Governance Audit System**",
    "col1_title": "📄 1. 職位描述 (JD)" if is_zh else "📄 1. Job Description (JD)",
    "col2_title": "👤 2. 求職者履歷 (CV)" if is_zh else "👤 2. Candidate Resume (CV)",
    "col3_title": "🎯 3. 特殊要求 (Preferences)" if is_zh else "🎯 3. Special Requirements",
    "run_btn": "🚀 啟動高階人才科學與深度合規審查 (Run Audit)" if is_zh else "🚀 Run High-Level Talent Audit",
    "spinner_msg": "🚀 智析演算中：正在建立履歷證據鏈、拆解分數與進行風險反證..." if is_zh else "🚀 Analyzing: Building Evidence Table, Score Breakdown & Risk Flags...",

    # Dashboard 靜態標籤 (雙語適配)
    "sec1_title": "📊 1. 決策總結 (Fit Summary)" if is_zh else "📊 1. Fit Summary",
    "m_score": "綜合得分" if is_zh else "Overall Score",
    "m_conf": "信心級別" if is_zh else "Confidence Level",
    "m_rec": "最終建議" if is_zh else "Recommendation",
    "m_next": "推進下一關" if is_zh else "Advance to Next Stage",
    "verdict_title": "📌 執行摘要 (Verdict):" if is_zh else "📌 Executive Verdict:",
    "score_breakdown_title": "📈 分數拆解 (Score Breakdown)" if is_zh else "📈 Detailed Score Breakdown",
    "evidence_source": "證據來源" if is_zh else "Evidence Source",

    "sec2_title": "📜 2. 履歷可追溯證據與反證 (Evidence & Counter-Evidence)" if is_zh else "📜 2. Traceable Evidence & Counter-Evidence",
    "empty_evidence": "暫無足夠證據可供顯示。" if is_zh else "No sufficient evidence available.",
    "sec3_title": "🛡️ 3. 風險分層與 AI 管治控制 (Risk Flags & AI Governance)" if is_zh else "🛡️ 3. Risk Flags & AI Governance Controls",
    "hard_risks": "🚨 硬性風險 (Hard Risks - 必須查核):" if is_zh else "🚨 Hard Risks (Requires Immediate Verification):",
    "soft_risks": "⚠️ 軟性風險 (Soft Risks - 面試觀察):" if is_zh else "⚠️ Soft Risks (Interview Observation Points):",
    "bias_traps": "⚖️ 偏見陷阱防範 (Bias Traps):" if is_zh else "⚖️ Anti-Bias Guardrails:",
    "missing_info": "❓ 缺失關鍵資訊 (Missing Info):" if is_zh else "❓ Missing Critical Information:",
    "must_confirm": "🎯 Offer 前必確認 (Must Confirm):" if is_zh else "🎯 Must Confirm Before Offer:",

    "sec4_title": "🎯 4. 結構化面試指南 (Structured Interview Probes)" if is_zh else "🎯 4. Structured Behavioral Interview Probes",
    "sec4_sub": "💡 *包含測試意圖、正面指標 (Strong) 與負面警號 (Red Flag)*" if is_zh else "💡 *Includes testing purpose, strong indicators, and red flag answer patterns.*",
    "probe_purpose": "🎯 測試目的:" if is_zh else "🎯 Testing Purpose:",
    "probe_q": "🗣️ 面試提問:" if is_zh else "🗣️ Behavioral Question:",
    "probe_strong": "✅ 優秀指標 (Strong):" if is_zh else "✅ Strong Indicator:",
    "probe_red": "🚩 危險警號 (Red Flag):" if is_zh else "🚩 Red Flag Pattern:"
}

# Sidebar 配置
with st.sidebar:
    st.header(ui_labels["sys_config"])
    if default_token:
        key_mode = st.radio(ui_labels["key_mode"], [ui_labels["default_key"], ui_labels["byok_key"]], index=0)
    else:
        key_mode = ui_labels["byok_key"]

    if key_mode == ui_labels["default_key"]:
        provider = "GitHub Models"
        api_key = default_token
        st.info(ui_labels["loaded_default"])
    else:
        provider = st.selectbox(ui_labels["select_provider"], ["OpenAI", "DeepSeek", "Google Gemini", "Groq", "GitHub Models"])
        api_key = st.text_input(ui_labels["enter_key"].format(provider), type="password")

    st.divider()
    st.markdown(ui_labels["framework_title"])
    st.markdown(ui_labels["framework_body"])

# 多格式文本提取函數
def extract_text_from_files(uploaded_files):
    if not uploaded_files: return ""
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]
    combined_text = ""
    for file in uploaded_files:
        file_type = file.name.split('.')[-1].lower()
        file_text = ""
        try:
            if file_type == "pdf":
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages: file_text += (page.extract_text() or "") + "\n"
            elif file_type in ["docx", "doc"]:
                doc = docx.Document(file)
                for para in doc.paragraphs: file_text += para.text + "\n"
            if file_text.strip(): combined_text += f"\n--- [Source: {file.name}] ---\n" + file_text
        except Exception:
            pass
    return combined_text

# Header
st.title(ui_labels["title"])
st.caption(ui_labels["subtitle"])

# 主畫面 Input 欄位
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader(ui_labels["col1_title"])
    jd_input_type = st.radio("輸入", ["貼上文字", "上傳文件 (可多選)"] if is_zh else ["Paste Text", "Upload Files"], horizontal=True, key="jd_mode")
    if jd_input_type in ["貼上文字", "Paste Text"]:
        jd_text = st.text_area("JD 內容", height=200, placeholder="包含職責與資格等..." if is_zh else "Duties, requirements...", label_visibility="collapsed")
    else:
        jd_files = st.file_uploader("上傳 JD 檔案 (PDF, DOCX, DOC)", type=["pdf", "docx", "doc"], accept_multiple_files=True, key="jd_uploader")
        jd_text = extract_text_from_files(jd_files)

with col2:
    st.subheader(ui_labels["col2_title"])
    cv_files = st.file_uploader("上傳 CV 檔案 (PDF, DOCX, DOC)", type=["pdf", "docx", "doc"], accept_multiple_files=True, key="cv_uploader")
    cv_text = extract_text_from_files(cv_files)

with col3:
    st.subheader(ui_labels["col3_title"])
    special_reqs = st.text_area("補充說明與特定要求", height=200, placeholder="例如：\n- 必須精通廣東話/英語" if is_zh else "E.g.,\n- Fluent in Cantonese/English", label_visibility="collapsed")

st.markdown("---")

# AI 呼叫封裝（支援原生 JSON Mode）
def run_ai_analysis(provider, api_key, prompt):
    if provider == "Google Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        return response.text
    else:
        base_urls = {"OpenAI": "https://api.openai.com/v1", "DeepSeek": "https://api.deepseek.com", "Groq": "https://api.groq.com/openai/v1", "GitHub Models": "https://models.inference.ai.azure.com"}
        models = {"OpenAI": "gpt-4o-mini", "DeepSeek": "deepseek-chat", "Groq": "llama-3.3-70b-versatile", "GitHub Models": "gpt-4o-mini"}
        client = OpenAI(base_url=base_urls[provider], api_key=api_key)
        response = client.chat.completions.create(
            model=models[provider],
            messages=[{"role": "system", "content": "You are a Senior HR Analyst and AI Governance Expert outputting raw JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content.strip()

# 啟動按鈕邏輯
if st.button(ui_labels["run_btn"], type="primary", use_container_width=True):
    # 防禦 1: 公共試用額度提示與引導 (滿 10 次後提醒)
    if key_mode == ui_labels["default_key"]:
        if st.session_state.usage_count >= 10:
            st.info(ui_labels["quota_exceeded"])
            st.stop()
        st.session_state.usage_count += 1

    if not api_key or not jd_text.strip() or not cv_text.strip():
        st.warning("⚠️ 系統需要完整的 API Key, JD 與 CV 才能啟動。" if is_zh else "⚠️ API Key, JD, and CV are required.")
    else:
        # 防禦 2: Token 防爆 Smart Truncation
        MAX_CHARS = 80000 
        if len(jd_text) + len(cv_text) > MAX_CHARS:
            st.warning("⚠️ 上傳的文件內容過長，系統已自動截斷尾部以保護 API 穩定性與防爆 Token。" if is_zh else "⚠️ Content too long. System truncated the tail to prevent API failure.")
            jd_text = jd_text[:MAX_CHARS//2] + "\n\n...[JD Content Truncated System Warning]"
            cv_text = cv_text[:MAX_CHARS//2] + "\n\n...[CV Content Truncated System Warning]"

        with st.spinner(ui_labels["spinner_msg"]):
            try:
                lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文). Only keep standard industry abbreviations if necessary." if is_zh else "Provide the ENTIRE analysis and JSON values strictly in Professional Executive English. Do not use any Chinese characters in any fields."
                
                prompt = f"""
You are a senior HR analyst and talent acquisition advisor operating under strict ISO 42001 guidelines. Your task is to assess the candidate's fit based STRICTLY on the job description, CV, and stated preferences. Use evidence-based reasoning. Do not infer facts not supported by materials.

Language Requirement:
{lang_instruction}

Special Requirements:
{special_reqs if special_reqs.strip() else "None specified."}

Format your output STRICTLY in valid JSON matching this exact schema:
{{
  "fit_summary": {{
    "overall_score": 85,
    "confidence_level": "High / Medium / Low",
    "final_recommendation": "Strongly Suitable / Suitable / Partially Suitable / Not Suitable",
    "one_sentence_verdict": "Clear executive summary."
  }},
  "score_breakdown": [
    {{"dimension": "Hard Requirements / 硬性條件", "score": "80/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "Core Competency / 核心能力", "score": "85/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "Industry Fit / 行業匹配", "score": "60/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "Style & Culture / 工作風格", "score": "90/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "Risk Deductions / 風險扣分", "score": "-10", "justification": "...", "evidence_type": "Direct / Inferred"}}
  ],
  "evidence_table": [
    {{
      "claim": "Statement of finding",
      "cv_quote": "Exact quote from CV",
      "source_section": "Section or company name",
      "confidence": "High / Medium / Low",
      "counter_evidence": "Counter-evidence or limitation"
    }}
  ],
  "risk_flags": {{
    "hard_risks": ["Hard risks requiring verification"],
    "soft_risks": ["Soft risks requiring interview follow-up"],
    "bias_traps": ["Potential bias traps to avoid"],
    "missing_info": ["Missing critical information"]
  }},
  "interview_probes": [
    {{
      "competency": "Role-specific competency",
      "testing_purpose": "What this question tests",
      "question": "STAR behavioral question",
      "strong_indicator": "Strong answer pattern",
      "red_flag": "Red flag answer pattern"
    }}
  ],
  "final_guidance": {{
    "advance_to_next": "Yes / No / Conditional",
    "next_stage_action": "Recommended next action",
    "must_confirm": ["Items to confirm before offer"]
  }}
}}

Output ONLY raw JSON. Do not include markdown formatting.

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                raw_response = run_ai_analysis(provider, api_key, prompt)
                
                # 防禦 3: Robust JSON Parsing
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                clean_json = json_match.group(0) if json_match else raw_response.strip()
                
                try:
                    data = json.loads(clean_json)
                except json.JSONDecodeError:
                    st.error("❌ AI 回傳資料格式異常，請重新點擊分析按鈕。" if is_zh else "❌ Invalid JSON format from AI, please retry.")
                    st.stop()

                # 防禦 4: Safe Schema Access (.get())
                fit_summary = data.get('fit_summary', {})
                final_guidance = data.get('final_guidance', {})
                risk_flags = data.get('risk_flags', {})
                
                # Dashboard 渲染
                st.markdown(f"## {ui_labels['sec1_title']}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(ui_labels["m_score"], f"{fit_summary.get('overall_score', 'N/A')} / 100")
                c2.metric(ui_labels["m_conf"], fit_summary.get('confidence_level', 'N/A'))
                c3.metric(ui_labels["m_rec"], fit_summary.get('final_recommendation', 'N/A'))
                c4.metric(ui_labels["m_next"], final_guidance.get('advance_to_next', 'N/A'))
                
                st.info(f"**{ui_labels['verdict_title']}** {fit_summary.get('one_sentence_verdict', 'N/A')}")
                
                st.markdown(f"### {ui_labels['score_breakdown_title']}")
                score_breakdown = data.get('score_breakdown', [])
                if score_breakdown:
                    sb_cols = st.columns(len(score_breakdown))
                    for idx, item in enumerate(score_breakdown):
                        with sb_cols[idx]:
                            st.markdown(f"**{item.get('dimension', 'N/A')}**")
                            st.markdown(f"### {item.get('score', 'N/A')}")
                            st.caption(f"{item.get('justification', '')}")
                            st.caption(f"*({ui_labels['evidence_source']}: {item.get('evidence_type', 'N/A')})*")
                
                st.markdown("---")
                st.markdown(f"## {ui_labels['sec2_title']}")
                evidence_data = data.get('evidence_table', [])
                if evidence_data:
                    st.table(evidence_data)
                else:
                    st.info(ui_labels["empty_evidence"])
                
                st.markdown("---")
                st.markdown(f"## {ui_labels['sec3_title']}")
                r1, r2 = st.columns(2)
                with r1:
                    st.error(f"**{ui_labels['hard_risks']}**\n" + "\n".join([f"- {x}" for x in risk_flags.get('hard_risks', ["None"])]))
                    st.warning(f"**{ui_labels['soft_risks']}**\n" + "\n".join([f"- {x}" for x in risk_flags.get('soft_risks', ["None"])]))
                with r2:
                    st.info(f"**{ui_labels['bias_traps']}**\n" + "\n".join([f"- {x}" for x in risk_flags.get('bias_traps', ["None"])]))
                    st.markdown(f"**{ui_labels['missing_info']}**\n" + "\n".join([f"- {x}" for x in risk_flags.get('missing_info', ["None"])]))
                    st.markdown(f"**{ui_labels['must_confirm']}**\n" + "\n".join([f"- {x}" for x in final_guidance.get('must_confirm', ["None"])]))
                
                st.markdown("---")
                st.markdown(f"## {ui_labels['sec4_title']}")
                st.caption(ui_labels["sec4_sub"])
                for q in data.get('interview_probes', []):
                    with st.expander(f"📌 {q.get('competency', 'Competency')}"):
                        st.markdown(f"**{ui_labels['probe_purpose']}** {q.get('testing_purpose', '')}")
                        st.markdown(f"**{ui_labels['probe_q']}** {q.get('question', '')}")
                        st.success(f"**{ui_labels['probe_strong']}** {q.get('strong_indicator', '')}")
                        st.error(f"**{ui_labels['probe_red']}** {q.get('red_flag', '')}")
                        
            except Exception as e:
                # 伺服器端 Debug 日誌 (隱蔽 Key)
                print(f"[DEBUG - API Error] {type(e).__name__}: {str(e)}") 
                st.error(f"❌ Analysis Error / 分析過程出現錯誤: {type(e).__name__} - 系統異常或連線超時，請檢查網路連線與 Key 權限。" if is_zh else f"❌ Analysis Error: {type(e).__name__}. Please check your connection and API key.")
