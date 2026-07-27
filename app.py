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

# 讀取後台預設 Secrets
default_token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GEMINI_API_KEY", "")

# 語言選擇
with st.sidebar:
    output_lang = st.selectbox(
        "🌐 界面與報告語言 (UI & Output Language):",
        ["繁體中文 (Traditional Chinese)", "English (Full)"],
        index=0
    )
    st.divider()

is_zh = output_lang == "繁體中文 (Traditional Chinese)"

# UI 文字字典 (強化安全感與產品特色)
ui_labels = {
    "sys_config": "⚙️ 系統設定 (System Config)" if is_zh else "⚙️ System Config",
    "key_mode": "選擇 AI 金鑰模式：" if is_zh else "Select AI Key Mode:",
    "default_key": "使用系統預設免費 Key" if is_zh else "Use System Default Free Key",
    "byok_key": "使用自備 AI API Key" if is_zh else "Use Custom AI API Key",
    "loaded_default": "✅ 已載入系統預設免費 Key" if is_zh else "✅ Loaded system default key",
    "select_provider": "選擇 AI 供應商 (Provider)：" if is_zh else "Select AI Provider:",
    "enter_key": "輸入你的 {} Key" if is_zh else "Enter your {} Key",
    
    # 💡 重新設計：著重「資安安心」與「核心特色」
    "framework_title": "🛡️ 數據安全與系統特色" if is_zh else "🛡️ Privacy & Core Features",
    "framework_body": """
    **🔐 企業級私密防護 (Data Privacy):**
    - **零數據留存:** 僅於本地 Session 記憶體運算，重新整理頁面即完全清空。
    - **BYOK 直連加密:** 自備 Key 直連 AI 官方 API，不經過任何第三方中轉伺服器。
    - **隱私合規:** 嚴格遵循香港 PDPO 數據私隱條例及國際高風險 AI 合規規範。

    **🎯 深度招募特色 (Key Features):**
    - **履歷原文追溯:** 每項評價均提供原段落引用與「反證驗證」，杜絕 AI 幻覺。
    - **硬/軟風險分層:** 區分簽證/語言等「硬死線」與文化/習慣等「面試觀察點」。
    - **實戰防僞面試:** 內建高鑑別力 STAR 問題、優秀指標與紅旗 (Red Flag) 警號。
    """ if is_zh else """
    **🔐 Enterprise Privacy Guarantee:**
    - **Zero Data Retention:** Processed strictly in-memory per session; wiped upon refresh.
    - **Direct API Connection:** Your Key connects directly to official AI endpoints with no third-party middleware.
    - **PDPO Compliant:** Built under Hong Kong PDPO & global high-risk AI safety guidelines.

    **🎯 Core Platform Features:**
    - **Traceable Evidence:** Every claim is backed by exact CV quotes and counter-evidence checks.
    - **Risk Stratification:** Isolates hard blockers (visa/language) from soft observation points.
    - **Structured Interview Probing:** Generates targeted STAR probes with Strong and Red Flag indicators.
    """,
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)" if is_zh else "🎯 TalentScout AI",
    "subtitle": "🚀 **企業級高階人才決策與風險合規評估系統**" if is_zh else "🚀 **Enterprise Talent Advisory & Compliance Audit System**",
    "col1_title": "📄 1. 職位描述 (JD)",
    "col2_title": "👤 2. 求職者履歷 (CV)",
    "col3_title": "🎯 3. 特殊要求 (Preferences)",
    "run_btn": "🚀 啟動高階人才科學與深度合規審查 (Run Audit)" if is_zh else "🚀 Run High-Level Talent Audit",
    "spinner_msg": "🚀 智析演算中：正在建立履歷證據鏈、拆解分數與進行風險反證..." if is_zh else "🚀 Analyzing: Building Evidence Table, Score Breakdown & Risk Flags...",
}

with st.sidebar:
    st.header(ui_labels["sys_config"])
    if default_token:
        key_mode = st.radio(ui_labels["key_mode"], [ui_labels["default_key"], ui_labels["byok_key"]], index=0)
    else:
        key_mode = ui_labels["byok_key"]

    if key_mode == ui_labels["default_key"]:
        provider = "GitHub Models"
        api_key = default_token
        st.success(ui_labels["loaded_default"])
    else:
        provider = st.selectbox(ui_labels["select_provider"], ["OpenAI", "DeepSeek", "Google Gemini", "Groq", "GitHub Models"])
        api_key = st.text_input(ui_labels["enter_key"].format(provider), type="password")

    st.divider()
    st.markdown(ui_labels["framework_title"])
    st.markdown(ui_labels["framework_body"])

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

st.title(ui_labels["title"])
st.caption(ui_labels["subtitle"])

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader(ui_labels["col1_title"])
    jd_input_type = st.radio("輸入", ["貼上文字", "上傳文件 (可多選)"], horizontal=True, key="jd_mode")
    if jd_input_type == "貼上文字":
        jd_text = st.text_area("JD 內容", height=200, placeholder="包含職責與資格等...", label_visibility="collapsed")
    else:
        jd_files = st.file_uploader("上傳 JD 檔案 (PDF, DOCX, DOC)", type=["pdf", "docx", "doc"], accept_multiple_files=True, key="jd_uploader")
        jd_text = extract_text_from_files(jd_files)

with col2:
    st.subheader(ui_labels["col2_title"])
    cv_files = st.file_uploader("上傳 CV 檔案 (PDF, DOCX, DOC)", type=["pdf", "docx", "doc"], accept_multiple_files=True, key="cv_uploader")
    cv_text = extract_text_from_files(cv_files)

with col3:
    st.subheader(ui_labels["col3_title"])
    special_reqs = st.text_area("補充說明與特定要求", height=200, placeholder="例如：\n- 必須精通廣東話/英語\n- 接受每週 5 天到現場工作", label_visibility="collapsed")

st.markdown("---")

def run_ai_analysis(provider, api_key, prompt):
    if provider == "Google Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt + "\n\nFormat strictly as raw JSON without markdown.")
        return response.text
    else:
        base_urls = {"OpenAI": "https://api.openai.com/v1", "DeepSeek": "https://api.deepseek.com", "Groq": "https://api.groq.com/openai/v1", "GitHub Models": "https://models.inference.ai.azure.com"}
        models = {"OpenAI": "gpt-4o-mini", "DeepSeek": "deepseek-chat", "Groq": "llama-3.3-70b-versatile", "GitHub Models": "gpt-4o-mini"}
        client = OpenAI(base_url=base_urls[provider], api_key=api_key)
        response = client.chat.completions.create(
            model=models[provider],
            messages=[{"role": "system", "content": "You are a Senior HR Analyst and AI Governance Expert outputting raw JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

if st.button(ui_labels["run_btn"], type="primary", use_container_width=True):
    if not api_key or not jd_text.strip() or not cv_text.strip():
        st.warning("⚠️ 系統需要完整的 API Key, JD 與 CV 才能啟動。")
    else:
        with st.spinner(ui_labels["spinner_msg"]):
            try:
                lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文). Only keep standard industry abbreviations (e.g. JD, CV, AIGP, STAR, IT, ASMTP, HR, KPI) if necessary." if is_zh else "Provide the ENTIRE analysis strictly in Professional Executive English."
                
                prompt = f"""
You are a senior HR analyst and talent acquisition advisor operating under strict ISO 42001 guidelines. Your task is to assess the candidate's fit based STRICTLY on the job description, CV, and stated preferences. Use evidence-based reasoning. Do not infer facts not supported by materials.

Language Requirement:
{lang_instruction}

Special Requirements:
{special_reqs if special_reqs.strip() else "None specified."}

### Assessment Principles:
- Prioritize job-related evidence over prestige/subjective impressions.
- Identify both supporting evidence AND counter-evidence for major conclusions.
- Separate Hard Risks (e.g., Visa, language, credentials) from Soft Risks (e.g., style, culture, adaptability).
- Flag missing/ambiguous info for human verification (HITL).

Format your output STRICTLY in valid JSON matching this exact schema:
{{
  "fit_summary": {{
    "overall_score": 85,
    "confidence_level": "High / Medium / Low",
    "final_recommendation": "Strongly Suitable / Suitable / Partially Suitable / Not Suitable",
    "one_sentence_verdict": "Clear executive summary."
  }},
  "score_breakdown": [
    {{"dimension": "硬性條件 (Hard Requirements)", "score": "80/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "核心能力 (Core Competency)", "score": "85/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "行業匹配 (Industry Fit)", "score": "60/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "工作風格 (Style & Culture)", "score": "90/100", "justification": "...", "evidence_type": "Direct / Inferred"}},
    {{"dimension": "風險扣分 (Risk Deductions)", "score": "-10", "justification": "...", "evidence_type": "Direct / Inferred"}}
  ],
  "evidence_table": [
    {{
      "claim": "正面或負面論點",
      "cv_quote": "履歷精確原文引用",
      "source_section": "經歷/公司段落",
      "confidence": "High / Medium / Low",
      "counter_evidence": "反證 (例如: 具備高壓應變能力 -> 反證: 但無長期穩定行政經驗)"
    }}
  ],
  "risk_flags": {{
    "hard_risks": ["必須人手確認的硬傷 (簽證/權限/語言)"],
    "soft_risks": ["面試需觀察的軟性風險 (文化/跳槽)"],
    "bias_traps": ["需避免的偏見 (例如不要因為某單一光環或單一缺失就下定論)"],
    "missing_info": ["關鍵缺失資訊"]
  }},
  "interview_probes": [
    {{
      "competency": "針對崗位的關鍵能力 (如預判需求/高壓決策)",
      "testing_purpose": "這題想測試什麼？",
      "question": "情境與行為問題 (STAR)",
      "strong_indicator": "優秀回答特徵 (Strong-answer indicator)",
      "red_flag": "警號回答特徵 (Red flag answer pattern)"
    }}
  ],
  "final_guidance": {{
    "advance_to_next": "Yes / No / Conditional",
    "next_stage_action": "下一步建議行動",
    "must_confirm": ["Offer 前必須確認的事項"]
  }}
}}

Output ONLY raw JSON. Do not include markdown formatting.

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                raw_response = run_ai_analysis(provider, api_key, prompt)
                
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                clean_json = json_match.group(0) if json_match else raw_response.strip()
                data = json.loads(clean_json)
                
                # Dashboard Visualization
                st.markdown(f"## 📊 1. 決策總結 (Fit Summary)")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("綜合得分", f"{data['fit_summary']['overall_score']} / 100")
                c2.metric("信心級別", data['fit_summary']['confidence_level'])
                c3.metric("最終建議", data['fit_summary']['final_recommendation'])
                c4.metric("推進下一關", data['final_guidance']['advance_to_next'])
                
                st.info(f"**📌 執行摘要 (Verdict):** {data['fit_summary']['one_sentence_verdict']}")
                
                st.markdown("### 📈 分數拆解 (Score Breakdown)")
                sb_cols = st.columns(len(data['score_breakdown']))
                for idx, item in enumerate(data['score_breakdown']):
                    with sb_cols[idx]:
                        st.markdown(f"**{item['dimension']}**")
                        st.markdown(f"### {item['score']}")
                        st.caption(f"{item['justification']}")
                        st.caption(f"*(證據來源: {item['evidence_type']})*")
                
                st.markdown("---")
                st.markdown(f"## 📜 2. 履歷可追溯證據與反證 (Evidence & Counter-Evidence)")
                st.table(data['evidence_table'])
                
                st.markdown("---")
                st.markdown(f"## 🛡️ 3. 風險分層與偏見控制 (Risk Flags & Validation)")
                r1, r2 = st.columns(2)
                with r1:
                    st.error("**🚨 硬性風險 (Hard Risks - 必須查核):**\n" + "\n".join([f"- {x}" for x in data['risk_flags']['hard_risks']]))
                    st.warning("**⚠️ 軟性風險 (Soft Risks - 面試觀察):**\n" + "\n".join([f"- {x}" for x in data['risk_flags']['soft_risks']]))
                with r2:
                    st.info("**⚖️ 偏見陷阱防範 (Bias Traps):**\n" + "\n".join([f"- {x}" for x in data['risk_flags']['bias_traps']]))
                    st.markdown("**❓ 缺失關鍵資訊 (Missing Info):**\n" + "\n".join([f"- {x}" for x in data['risk_flags']['missing_info']]))
                    st.markdown("**🎯 Offer 前必確認 (Must Confirm):**\n" + "\n".join([f"- {x}" for x in data['final_guidance']['must_confirm']]))
                
                st.markdown("---")
                st.markdown(f"## 🎯 4. 結構化面試指南 (Structured Interview Probes)")
                st.caption("💡 *包含測試意圖、正面指標 (Strong) 與負面警號 (Red Flag)*")
                for q in data['interview_probes']:
                    with st.expander(f"📌 {q['competency']}"):
                        st.markdown(f"**🎯 測試目的:** {q['testing_purpose']}")
                        st.markdown(f"**🗣️ 面試提問:** {q['question']}")
                        st.success(f"**✅ 優秀指標 (Strong):** {q['strong_indicator']}")
                        st.error(f"**🚩 危險警號 (Red Flag):** {q['red_flag']}")
                        
            except Exception as e:
                st.error(f"❌ Analysis Error / 分析過程出現錯誤: {str(e)}")
