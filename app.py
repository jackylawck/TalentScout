import streamlit as st
import pypdf
import json
from google import genai
from google.genai import types

# 頁面標題與配置
st.set_page_config(
    page_title="慧聘 · 智析官 (TalentScout AI)",
    page_icon="🎯",
    layout="wide"
)

# 系統標題與 Tagline
st.title("🎯 慧聘 · 智析官 (TalentScout AI)")
st.caption("🚀 **自備 Key・零風險・秒速匹配人才**｜基於 A+ 人才篩選架構、DEIB 原則與 STAR 行為面試法的高階 HR 智能副駕")

# Sidebar: 設定 API Key
with st.sidebar:
    st.header("⚙️ 系統設定 (BYOK)")
    api_key = st.text_input("輸入 Gemini API Key", type="password")
    st.markdown("[👉 取得免費 Gemini API Key](https://aistudio.google.com/)")
    st.divider()
    st.markdown("### 🛡️ 數據安全與管治聲明")
    st.markdown("""
    - **100% 本地 Session 運作：** 零數據庫儲存。
    - **隱私合規：** 符合香港《個人資料（私隱）條例》(PDPO) 指引。
    - **客觀結構化評分：** 降低面試官主觀偏見 (Bias)。
    """)

# PDF 文字提取函數
def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# 主介面：上傳與輸入區
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 1. 輸入職位描述 (JD)")
    jd_input_type = st.radio("JD 輸入方式", ["直接貼上文字", "上傳 PDF"], key="jd_type")
    
    jd_text = ""
    if jd_input_type == "直接貼上文字":
        jd_text = st.text_area("請貼上 JD 內容：", height=250, placeholder="包含職責、必備條件、軟實力要求等...")
    else:
        jd_file = st.file_uploader("上傳 JD PDF", type=["pdf"], key="jd_pdf")
        if jd_file:
            jd_text = extract_text_from_pdf(jd_file)

with col2:
    st.subheader("👤 2. 輸入求職者履歷 (CV)")
    cv_file = st.file_uploader("上傳求職者 CV (PDF 格式)", type=["pdf"], key="cv_pdf")
    cv_text = ""
    if cv_file:
        cv_text = extract_text_from_pdf(cv_file)
        st.success(f"已讀取 CV：{cv_file.name}")

st.markdown("---")

# 定義 Gemini JSON Schema（強制輸出結構化資料）
analysis_schema = {
    "type": "OBJECT",
    "properties": {
        "overall_score": {"type": "INTEGER", "description": "0-100 的整體匹配分數"},
        "recommendation": {"type": "STRING", "description": "極力推薦 / 可考慮面試 / 需補充資料 / 不建議"},
        "strengths": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "3 個最符合 JD 的核心優勢或量化成果"
        },
        "red_flags": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "潛在疑慮，如資歷空窗、跳槽頻率、Overqualified 或缺乏關鍵證照"
        },
        "competency_matrix": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "item": {"type": "STRING", "description": "評估項目"},
                    "jd_req": {"type": "STRING", "description": "JD 要求"},
                    "cv_match": {"type": "STRING", "description": "CV 狀況"},
                    "status": {"type": "STRING", "description": "Pass / Fail / Partial"}
                }
            }
        },
        "cultural_fit": {
            "type": "OBJECT",
            "properties": {
                "agility": {"type": "STRING", "description": "適應力與成長思維分析"},
                "style": {"type": "STRING", "description": "團隊與管理風格預估"}
            }
        },
        "deib_warning": {"type": "STRING", "description": "JD 或 CV 中是否包含年齡、性別、地域等偏見風險（若無則填「無顯著偏見風險」）"},
        "star_questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "target": {"type": "STRING", "description": "針對的能力疑點或亮點"},
                    "question": {"type": "STRING", "description": "STAR 面試題目"},
                    "what_to_look_for": {"type": "STRING", "description": "觀察重點與期望回答"}
                }
            }
        }
    },
    "required": ["overall_score", "recommendation", "strengths", "red_flags", "competency_matrix", "cultural_fit", "deib_warning", "star_questions"]
}

# 按鈕與分析邏輯
if st.button("🚀 啟動「慧聘 · 智析官」進行深度匹配", type="primary", use_container_width=True):
    if not api_key:
        st.error("請在左側 Sidebar 輸入 Gemini API Key！")
    elif not jd_text or not cv_text:
        st.warning("請確保已同時提供 JD 與 CV 內容！")
    else:
        with st.spinner("「慧聘 · 智析官」正在進行多維度矩陣分析與評分..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
你是一位擁有 20 年經驗的高階人力資源顧問 (HR Executive) 及 企業人才戰略專家。
請根據以下提供的 Job Description (JD) 與 Candidate CV，進行深度、客觀且專業的匹配分析，並依指定 JSON 格式回傳。

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""

                # 呼叫 Gemini 2.5 Flash 並使用 JSON Schema
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=analysis_schema,
                        temperature=0.2
                    ),
                )
                
                # 解析 JSON 結果
                data = json.loads(response.text)
                
                # 視覺化渲染 Dashboard
                st.markdown("## 📊 1. 綜合匹配與評估結果")
                
                m_col1, m_col2, m_col3 = st.columns([1, 1, 2])
                with m_col1:
                    st.metric(label="綜合匹配得分", value=f"{data['overall_score']} / 100")
                    st.progress(data['overall_score'] / 100)
                with m_col2:
                    st.metric(label="招聘建議", value=data['recommendation'])
                with m_col3:
                    st.info(f"🛡️ **DEIB / 偏見風險檢測：** {data['deib_warning']}")

                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.success("### ✅ 核心優勢 (Strengths)")
                    for s in data['strengths']:
                        st.markdown(f"- {s}")
                with res_col2:
                    st.warning("### ⚠️ 潛在風險 / 疑慮 (Red Flags)")
                    for r in data['red_flags']:
                        st.markdown(f"- {r}")

                st.markdown("---")
                st.markdown("## 🧩 2. 關鍵能力與門檻對比矩陣 (Competency Matrix)")
                st.dataframe(data['competency_matrix'], use_container_width=True)

                st.markdown("---")
                st.markdown("## 🎯 3. 人才畫像與文化契合度 (Persona & Fit)")
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.markdown("**🌱 適應力與成長思維 (Agility):**")
                    st.write(data['cultural_fit']['agility'])
                with p_col2:
                    st.markdown("**🤝 團隊與管理風格 (Leadership/Team Style):**")
                    st.write(data['cultural_fit']['style'])

                st.markdown("---")
                st.markdown("## ❓ 4. 結構化 STAR 面試題庫 (Interview Guide)")
                for idx, q in enumerate(data['star_questions'], 1):
                    with st.expander(f"題目 {idx}：{q['target']}"):
                        st.markdown(f"**🗣️ 面試提問：** {q['question']}")
                        st.markdown(f"**🎯 考察重點與期望回答：** {q['what_to_look_for']}")
                        
            except Exception as e:
                st.error(f"分析過程出現錯誤：{str(e)}")
