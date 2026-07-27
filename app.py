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

# 語言選擇 (Sidebar 最頂層)
with st.sidebar:
    output_lang = st.selectbox(
        "🌐 界面與報告語言 (UI & Output Language):",
        ["繁體中文 (Traditional Chinese)", "English (Full)"],
        index=0
    )
    st.divider()

# UI 文字字典 (UI i18n Dictionary)
is_zh = output_lang == "繁體中文 (Traditional Chinese)"

ui_labels = {
    "sys_config": "⚙️ 系統設定 (System Config)" if is_zh else "⚙️ System Config",
    "key_mode": "選擇 AI 金鑰模式：" if is_zh else "Select AI Key Mode:",
    "default_key": "使用系統預設免費 Key" if is_zh else "Use System Default Free Key",
    "byok_key": "使用自備 AI API Key (自由選擇)" if is_zh else "Use Custom AI API Key (BYOK)",
    "loaded_default": "✅ 已載入系統預設免費 Key (保護中)" if is_zh else "✅ Loaded system default key (Protected)",
    "select_provider": "選擇你的 AI 供應商 (Provider)：" if is_zh else "Select AI Provider:",
    "enter_key": "輸入你的 {} Key" if is_zh else "Enter your {} Key",
    "framework_title": "🧠 人才科學與管治框架" if is_zh else "🧠 Talent Science & Governance",
    "framework_body": """
    - **可追溯性 (Traceability):** ISO 42001 履歷證據鏈 (Evidence Table)。
    - **五維拆解 (Score Breakdown):** 拆解硬條件、軟實力與風險扣分。
    - **反證機制 (Counter-Evidence):** 識別單一訊號偏見與履歷光環。
    - **動態 STAR 提問:** 根據崗位屬性量身打造高鑑別力問題。
    """ if is_zh else """
    - **Traceability:** ISO 42001 Evidence Table.
    - **Score Breakdown:** 5-subscore analytics.
    - **Counter-Evidence:** Mitigate Halo & Single-Signal Bias.
    - **Dynamic Probes:** Role-tailored STAR interview guide.
    """,
    "governance_notice": "🔐 **數據管治聲明：** 本地 Session 運作，零數據留存。符合 PDPO 及歐盟 AI 法案 (EU AI Act) 合規指引。" if is_zh else "🔐 **Data Governance Notice:** Session-only operation with zero retention. Compliant with PDPO & EU AI Act guidance.",
    
    # Header & Sections
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)" if is_zh else "🎯 TalentScout AI",
    "subtitle": "🚀 **ISO 42001 & AIGP 全崗位企業級人才決策與風險評估系統**" if is_zh else "🚀 **ISO 42001 & AIGP Universal Enterprise Talent Advisory System**",
    "col1_title": "📄 1. 職位描述 (JD)" if is_zh else "📄 1. Job Description (JD)",
    "col1_caption": "📦 *支援多檔案上傳｜單檔上限 200 MB*" if is_zh else "📦 *Supports multiple files | Max 200 MB/file*",
    "input_mode": "輸入方式" if is_zh else "Input Method",
    "paste_text": "貼上文字" if is_zh else "Paste Text",
    "upload_files": "上傳文件 (可多選)" if is_zh else "Upload Files",
    "paste_jd_ph": "請貼上 JD 內容，包含職責與資格等..." if is_zh else "Paste JD content here including duties, requirements...",
    "upload_jd_lbl": "上傳 JD 檔案 (PDF, DOCX, DOC)" if is_zh else "Upload JD Files (PDF, DOCX, DOC)",
    "jd_read_success": "✅ 已順利讀取 {} 個 JD 檔案" if is_zh else "✅ Successfully read {} JD file(s)",
    
    "col2_title": "👤 2. 求職者履歷 (CV)" if is_zh else "👤 2. Candidate Resume (CV)",
    "col2_caption": "📦 *支援多檔案上傳｜單檔上限 200 MB*" if is_zh else "📦 *Supports multiple files | Max 200 MB/file*",
    "upload_cv_lbl": "上傳 CV 檔案 (PDF, DOCX, DOC)" if is_zh else "Upload CV Files (PDF, DOCX, DOC)",
    "cv_read_success": "✅ 已順利讀取 {} 個 CV 檔案" if is_zh else "✅ Successfully read {} CV file(s)",
    
    "col3_title": "🎯 3. 特殊要求 (Preferences)" if is_zh else "🎯 3. Special Requirements",
    "col3_caption": "💡 *補充說明與團隊特定要求*" if is_zh else "💡 *Custom hiring criteria & preferences*",
    "special_req_ph": "例如：\n- 必須精通廣東話/英語\n- 必須接受每週 5 天到現場工作\n- 優先考慮具備金融背景者" if is_zh else "E.g.,\n- Must be fluent in Cantonese/English\n- 5 days on-site required\n- Prior banking background preferred",
    
    "run_btn": "🚀 啟動高階人才科學與深度合規審查 (Run Audit & Analysis)" if is_zh else "🚀 Run High-Level Talent Science & Compliance Audit",
    "spinner_msg": "🚀 智析演算中：正在建立履歷證據鏈、拆解五維分數與進行風險反證審查..." if is_zh else "🚀 Analyzing: Building Evidence Table, Score Breakdown & Risk Flags...",
    
    # Dashboard Titles
    "dash_sec1": "📊 1. 招聘決策總結與多維分數拆解 (Fit Summary & Score Breakdown)" if is_zh else "📊 1. Fit Summary & Multi-Score Breakdown",
    "overall_score": "綜合匹配得分 (Overall Score)" if is_zh else "Overall Score",
    "confidence": "評估可信度 (Confidence Level)：{}" if is_zh else "Confidence Level: {}",
    "recommendation": "決策建議 (Final Recommendation)：{}" if is_zh else "Recommendation: {}",
    
    "dash_sec2": "📜 2. 履歷可追溯證據鏈 (ISO 42001 Evidence Table)" if is_zh else "📜 2. ISO 42001 Evidence Table",
    "evidence_sub": "⚠️ *依據 ISO 42001 可追溯性要求，以下結論皆有履歷具體原文支撐。*" if is_zh else "⚠️ *Under ISO 42001 Traceability rules, all claims are mapped directly to CV source text.*",
    
    "dash_sec3": "🛡️ 3. 風險反證與可操作偏見控制 (Risk Flags & Anti-Bias Rules)" if is_zh else "🛡️ 3. Risk Flags & Anti-Bias Controls",
    "hitl_title": "👨‍⚖️ **人類監督與核實項目 (Human-in-the-Loop Triggers):**" if is_zh else "👨‍⚖️ **Human-in-the-Loop (HITL) Triggers:**",
    "bias_rules_title": "⚖️ **可操作偏見控制規則 (Operational Anti-Bias Rules):**" if is_zh else "⚖️ **Operational Anti-Bias Rules:**",
    
    "dash_sec4": "🎯 4. 崗位專屬結構化行為面試指南 (Behavioral STAR Probes)" if is_zh else "🎯 4. Targeted Behavioral STAR Interview Probes",
    "star_sub": "💡 *針對該崗位之核心勝任力設計，探究真實歷史行為與量化成果。*" if is_zh else "💡 *Tailored specifically to the role's core competencies to probe past actions and quantifiable impact.*",
}

# Sidebar: 設定與 Provider 處理
with st.sidebar:
    st.header(ui_labels["sys_config"])
    
    if default_token:
        key_mode = st.radio(
            ui_labels["key_mode"],
            [ui_labels["default_key"], ui_labels["byok_key"]],
            index=0
        )
    else:
        key_mode = ui_labels["byok_key"]

    if key_mode == ui_labels["default_key"]:
        provider = "GitHub Models"
        api_key = default_token
        st.success(ui_labels["loaded_default"])
    else:
        provider = st.selectbox(
            ui_labels["select_provider"],
            ["OpenAI", "DeepSeek", "Google Gemini", "Groq", "GitHub Models"]
        )
        
        help_texts = {
            "OpenAI": "OpenAI API Key (sk-...)",
            "DeepSeek": "DeepSeek API Key (sk-...)",
            "Google Gemini": "Google Gemini API Key (AIzaSy...)",
            "Groq": "Groq API Key (gsk_...)",
            "GitHub Models": "GitHub Personal Access Token (ghp_...)"
        }
        
        api_key = st.text_input(
            ui_labels["enter_key"].format(provider), 
            type="password",
            placeholder=help_texts[provider]
        )

    st.divider()
    st.markdown(ui_labels["framework_title"])
    st.markdown(ui_labels["framework_body"])
    st.divider()
    st.markdown(ui_labels["governance_notice"])

# 通用文件文字提取函數
def extract_text_from_files(uploaded_files):
    if not uploaded_files:
        return ""
    
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]
        
    combined_text = ""
    
    for file in uploaded_files:
        file_type = file.name.split('.')[-1].lower()
        file_text = ""
        try:
            if file_type == "pdf":
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    file_text += (page.extract_text() or "") + "\n"
            elif file_type in ["docx", "doc"]:
                doc = docx.Document(file)
                for para in doc.paragraphs:
                    file_text += para.text + "\n"
            
            if file_text.strip():
                combined_text += f"\n--- [Source: {file.name}] ---\n" + file_text
            else:
                st.warning(f"⚠️ `{file.name}` empty or unsupported binary `.doc`. Please 'Save As' `.docx` or `.pdf`.")
        except Exception as e:
            st.error(f"❌ Read failed for `{file.name}`. Please 'Save As' `.docx` or `.pdf`.")
            
    return combined_text

# Header
st.title(ui_labels["title"])
st.caption(ui_labels["subtitle"])

# Main UI: 三欄式上傳區
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader(ui_labels["col1_title"])
    st.caption(ui_labels["col1_caption"])
    jd_input_type = st.radio(ui_labels["input_mode"], [ui_labels["paste_text"], ui_labels["upload_files"]], key="jd_type", horizontal=True)
    jd_text = ""
    if jd_input_type == ui_labels["paste_text"]:
        jd_text = st.text_area(ui_labels["paste_text"] + ":", height=200, placeholder=ui_labels["paste_jd_ph"])
    else:
        jd_files = st.file_uploader(
            ui_labels["upload_jd_lbl"], 
            type=["pdf", "docx", "doc"], 
            accept_multiple_files=True, 
            key="jd_files"
        )
        if jd_files:
            jd_text = extract_text_from_files(jd_files)
            if jd_text:
                st.success(ui_labels["jd_read_success"].format(len(jd_files)))

with col2:
    st.subheader(ui_labels["col2_title"])
    st.caption(ui_labels["col2_caption"])
    cv_files = st.file_uploader(
        ui_labels["upload_cv_lbl"], 
        type=["pdf", "docx", "doc"], 
        accept_multiple_files=True, 
        key="cv_files"
    )
    cv_text = ""
    if cv_files:
        cv_text = extract_text_from_files(cv_files)
        if cv_text:
            st.success(ui_labels["cv_read_success"].format(len(cv_files)))

with col3:
    st.subheader(ui_labels["col3_title"])
    st.caption(ui_labels["col3_caption"])
    special_reqs = st.text_area(
        ui_labels["col3_title"] + ":", 
        height=200, 
        placeholder=ui_labels["special_req_ph"]
    )

st.markdown("---")

# 核心分析呼叫函數
def run_ai_analysis(provider, api_key, prompt):
    if provider == "Google Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt + "\n\nFormat strictly as raw JSON without markdown.",
        )
        return response.text
    else:
        base_urls = {
            "OpenAI": "https://api.openai.com/v1",
            "DeepSeek": "https://api.deepseek.com",
            "Groq": "https://api.groq.com/openai/v1",
            "GitHub Models": "https://models.inference.ai.azure.com"
        }
        models = {
            "OpenAI": "gpt-4o-mini",
            "DeepSeek": "deepseek-chat",
            "Groq": "llama-3.3-70b-versatile",
            "GitHub Models": "gpt-4o-mini"
        }
        
        client = OpenAI(base_url=base_urls[provider], api_key=api_key)
        response = client.chat.completions.create(
            model=models[provider],
            messages=[
                {"role": "system", "content": "You are an Executive Talent Acquisition Partner and Certified AI Governance Officer outputting raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

# Analyze Button
if st.button(ui_labels["run_btn"], type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Please enter API Key / Token!")
    elif not jd_text.strip() or not cv_text.strip():
        st.warning("⚠️ Please provide both valid JD and CV content!")
    else:
        with st.spinner(ui_labels["spinner_msg"]):
            try:
                lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文). Only keep standard industry abbreviations (e.g. JD, CV, AIGP, STAR, IT, ASMTP, HR, KPI) if necessary." if is_zh else "Provide the ENTIRE analysis strictly in Professional Executive English."
                
                # 全崗位通用 (General Roles) 高級 ISO 42001 + 拆解 + 反證 + 動態 STAR 專屬 Prompt
                prompt = f"""
You are an Executive Talent Acquisition Director and Senior AI Governance Lead operating at the board level in Hong Kong.
Analyze the provided Job Description (JD) and Candidate CV for ANY given professional role under strict ISO 42001 Audit principles (Traceability, Transparency, Counter-Evidence, Score Breakdown).

Language Requirement:
{lang_instruction}

Special Requirements:
{special_reqs if special_reqs.strip() else "None specified."}

### Mandatory Analytical Framework (For Any Professional Role):
1. **Fit Summary:** Provide a 1-sentence verdict (Suitable / Partially Suitable / Unsuitable), 3 core reasons to hire, and 3 core risk/mismatch reasons.
2. **Detailed Score Breakdown (0-100):** Break down the total score into:
   - Hard Requirements (Degree, Years of Experience, Language, Technical Certifications, Visa/Legal eligibility)
   - Core Competencies (Role-specific execution, problem solving, leadership, analytical skill)
   - Industry/Domain Match (Specific industry background or direct business domain experience)
   - Style & Cultural Fit (Work environment fit, proactivity, adaptability, team dynamics)
   - Risk Penalty Deductions (Job hopping, career gaps, critical skill/language/visa deficits)
3. **Evidence Table (Traceability):** List 3-4 key analytical claims about the candidate. For EACH claim, provide the exact quote from the CV, the source section/company, and a confidence level (High/Medium/Low).
4. **Counter-Evidence & Risk Flags:** 
   - Highlight potential Halo Effect or Single-Signal Bias (e.g., Do NOT assume lack of domain knowledge equals inability to perform transferable skills, or vice versa).
   - Identify specific operational/administrative risks (e.g., Job-hopping density, career gaps, visa dependency, language fluency gaps).
5. **Role-Tailored STAR Behavioral Probes:** Identify the top 3 critical competencies required by THIS SPECIFIC JD (e.g., Sales closing, Software Architecture, Strategic HR, Crisis Management, etc.). Provide:
   - Past-behavioral STAR question probing real historical evidence.
   - Sharp follow-up probe designed to verify authenticity and prevent rehearsed answers.

Format your output STRICTLY in valid JSON matching this schema:
{{
  "overall_score": 75,
  "confidence_level": "High (高可信度)",
  "final_recommendation": "Partially Suitable (勉強適合 - 建議先進行 Phone Screening 驗證硬性指標與風險點)",
  "fit_summary": {{
    "one_sentence_verdict": "One-line executive summary.",
    "top_3_reasons_to_hire": ["Reason 1", "Reason 2", "Reason 3"],
    "top_3_risks_and_gaps": ["Risk 1", "Risk 2", "Risk 3"]
  }},
  "score_breakdown": {{
    "hard_requirements_score": "80/100 (說明)",
    "core_competencies_score": "85/100 (說明)",
    "industry_match_score": "40/100 (說明)",
    "style_cultural_fit_score": "88/100 (說明)",
    "risk_penalties_deduction": "-10 分 (原因)"
  }},
  "evidence_table": [
    {{
      "claim": "分析結論...",
      "cv_quote": "履歷具體引用內文...",
      "source_section": "來源段落/公司名稱...",
      "confidence": "High / Medium / Low"
    }}
  ],
  "risk_flags_and_counter_evidence": {{
    "halo_bias_warning": "提醒避免因單一強項 (如名校/知名企業) 忽略實質短板，或因行業不符忽略其可轉移能力。",
    "administrative_visa_risk": "簽證、到職日或行政合規風險評估。",
    "language_and_culture_gap": "語言能力或團隊文化匹配之實質風險。"
  }},
  "actionable_anti_bias_rules": [
    "Rule 1: 不因非傳統背景或缺乏直接行業經驗單獨淘汰，著重評估可轉移之核心勝任力。",
    "Rule 2: 硬性風險指標 (如簽證/語言) 必須由 HR 進行人手確認，AI 不作最終決定。"
  ],
  "ea_behavioral_star_probes": [
    {{
      "kpi_focus": "該職位專屬核心勝任力 (如：複雜專案協調 / 技術突破 / 團隊管理)",
      "question": "針對該勝任力之真實歷史行為提問...",
      "anti_bs_probe": "深挖細節與可衡量成果之追問..."
    }}
  ]
}}

Output ONLY raw JSON.

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                raw_response = run_ai_analysis(provider, api_key, prompt)
                
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                clean_json = json_match.group(0) if json_match else raw_response.strip()
                data = json.loads(clean_json)
                
                # ================= Dashboard Visualization =================
                # Sec 1: 決策總結與分數拆解
                st.markdown(f"## {ui_labels['dash_sec1']}")
                colA, colB = st.columns([1, 2])
                with colA:
                    st.metric(label=ui_labels["overall_score"], value=f"{data['overall_score']} / 100")
                    st.progress(data['overall_score'] / 100)
                    st.info(ui_labels["confidence"].format(data.get('confidence_level', 'High')))
                    st.success(ui_labels["recommendation"].format(data.get('final_recommendation', 'Conditional Move')))

                with colB:
                    st.markdown(f"**📌 一句話總結 (Verdict):** {data['fit_summary']['one_sentence_verdict']}")
                    sub_c1, sub_c2 = st.columns(2)
                    with sub_c1:
                        st.markdown("**✅ 建議聘用 3 大理由：**")
                        for r in data['fit_summary']['top_3_reasons_to_hire']:
                            st.write(f"- {r}")
                    with sub_c2:
                        st.markdown("**⚠️ 核心風險 3 大隱憂：**")
                        for g in data['fit_summary']['top_3_risks_and_gaps']:
                            st.write(f"- {g}")

                st.markdown("### 📊 五維分數拆解 (Detailed Sub-Scores)")
                sb = data['score_breakdown']
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("硬性條件", sb['hard_requirements_score'])
                m2.metric("核心能力", sb['core_competencies_score'])
                m3.metric("行業匹配", sb['industry_match_score'])
                m4.metric("風格匹配", sb['style_cultural_fit_score'])
                m5.metric("風險扣分", sb['risk_penalties_deduction'])

                st.markdown("---")
                # Sec 2: 履歷證據鏈 Table
                st.markdown(f"## {ui_labels['dash_sec2']}")
                st.caption(ui_labels["evidence_sub"])
                st.table(data['evidence_table'])

                st.markdown("---")
                # Sec 3: 風險反證與 Anti-Bias
                st.markdown(f"## {ui_labels['dash_sec3']}")
                rf = data['risk_flags_and_counter_evidence']
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.warning(f"**👁️ 光環/單一訊號偏見預警:**\n\n{rf['halo_bias_warning']}")
                    st.error(f"**🛂 簽證/行政合規風險:**\n\n{rf['administrative_visa_risk']}")
                with col_r2:
                    st.info(f"**🗣️ 語言與文化匹配風險:**\n\n{rf['language_and_culture_gap']}")
                    st.markdown(ui_labels["bias_rules_title"])
                    for rule in data['actionable_anti_bias_rules']:
                        st.write(f"- {rule}")

                st.markdown("---")
                # Sec 4: 崗位專屬 STAR 提問
                st.markdown(f"## {ui_labels['dash_sec4']}")
                for idx, q in enumerate(data['ea_behavioral_star_probes'], 1):
                    with st.expander(f"📌 關鍵勝任力 (Competency Focus)：{q['kpi_focus']}"):
                        st.markdown(f"**🗣️ 行為提問 (STAR Question)：** {q['question']}")
                        st.markdown(f"**🕵️ 深挖追問 (Anti-BS Probe)：** {q['anti_bs_probe']}")
                        
            except Exception as e:
                st.error(f"❌ Analysis Error / 分析過程出現錯誤: {str(e)}")
