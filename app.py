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

# 系統標題
st.title("🎯 慧聘 · 智析官 (TalentScout AI) - 終極大師版")
st.caption("🚀 **自備 Key・零風險**｜融入冰山理論、阿里 ABC 人才分級與高階 STAR 面試法")

# Sidebar: 設定 API Key
with st.sidebar:
    st.header("⚙️ 系統設定 (BYOK)")
    api_key = st.text_input("輸入 Gemini API Key", type="password")
    st.markdown("[👉 點此免費申請 Gemini API Key](https://aistudio.google.com/)")
    st.divider()
    st.markdown("### 🧠 內建大師級招聘模型")
    st.markdown("""
    - **漏斗過濾：** 精準辨識 Must-haves。
    - **冰山理論：** 探測水面下的內驅力與價值觀。
    - **阿里 ABC 分級：** A類(超預期)、B類(符預期)、C類(不達標)。
    - **高階 STAR 追問：** 專攻挫折應對與底層邏輯。
    """)

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
    jd_input_type = st.radio("JD 輸入方式", ["直接貼上文字", "上傳 PDF"], key="jd_type", horizontal=True)
    jd_text = ""
    if jd_input_type == "直接貼上文字":
        jd_text = st.text_area("請貼上 JD 內容：", height=200)
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

# 升級版 JSON Schema (強制 AI 輸出高階分析結構)
analysis_schema = {
    "type": "OBJECT",
    "properties": {
        "overall_score": {"type": "INTEGER", "description": "0-100 的整體匹配分數"},
        "abc_classification": {"type": "STRING", "description": "A類(超出預期，堅決拿下) / B類(符合預期，可培養) / C類(達不到要求，堅決淘汰)"},
        "iceberg_analysis": {
            "type": "OBJECT",
            "properties": {
                "surface_skills": {"type": "STRING", "description": "冰山之上 (表象)：知識、技能、經驗是否達標？"},
                "deep_potential": {"type": "STRING", "description": "冰山之下 (潛在)：從經歷推斷其價值觀、內驅力、抗壓力與底層素養。"}
            }
        },
        "core_strengths": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "3 個最符合 JD 的核心優勢 (業績結果)"
        },
        "red_flags": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "可能隱藏的風險 (如經驗造假疑慮、頻繁跳槽、動機不明等)"
        },
        "star_questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "scenario": {"type": "STRING", "description": "針對的 CV 經歷或疑點"},
                    "question": {"type": "STRING", "description": "STAR 面試題 (必須包含詢問遇到的困難/挫折)"},
                    "what_to_look_for": {"type": "STRING", "description": "考官觀察重點 (業績=態度×能力，如何從回答判斷其態度與底層邏輯)"}
                }
            }
        }
    },
    "required": ["overall_score", "abc_classification", "iceberg_analysis", "core_strengths", "red_flags", "star_questions"]
}

# 分析按鈕
if st.button("🚀 啟動「大師級智能匹配」", type="primary", use_container_width=True):
    if not api_key:
        st.error("請在左側 Sidebar 輸入 Gemini API Key！")
    elif not jd_text or not cv_text:
        st.warning("請確保已同時提供 JD 與 CV 內容！")
    else:
        with st.spinner("AI 正在使用冰山理論與阿里招聘心法進行深度透視分析..."):
            try:
                client = genai.Client(api_key=api_key)
                
                # 升級版 Prompt，注入高階 HR 理論
                prompt = f"""
你是一位精通「冰山理論」、「阿里招聘邏輯」及「STAR 行為面試法」的頂尖人力資源總監。
請嚴格根據以下 JD 與 CV 進行深度透視，不僅看表面字眼，更要洞察底層邏輯：

1. **ABC 人才分級：** 嚴格評估此人是 A類(超預期)、B類(符預期) 還是 C類(不達標)。
2. **冰山理論透視：** 分析其水面上的技能，並推測水面下的內驅力與抗壓性。
3. **STAR 高階提問：** 設計面試題時，不問「有沒有做過」，而是問「怎麼做、遇到什麼挫折、如何克服」，以此考核其底層素質。

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=analysis_schema,
                        temperature=0.2
                    ),
                )
                
                data = json.loads(response.text)
                
                # 視覺化 Dashboard
                st.markdown("## 📊 1. 綜合決策與人才分級")
                colA, colB = st.columns(2)
                with colA:
                    st.metric(label="綜合匹配得分", value=f"{data['overall_score']} / 100")
                    st.progress(data['overall_score'] / 100)
                with colB:
                    # 依據 ABC 給予不同顏色的提示
                    abc_class = data['abc_classification']
                    if "A類" in abc_class:
                        st.success(f"🏆 **人才分級：** {abc_class}")
                    elif "B類" in abc_class:
                        st.info(f"👍 **人才分級：** {abc_class}")
                    else:
                        st.error(f"⚠️ **人才分級：** {abc_class}")

                st.markdown("---")
                st.markdown("## 🏔️ 2. 冰山模型深度透視 (Iceberg Analysis)")
                ice1, ice2 = st.columns(2)
                with ice1:
                    st.info(f"**🌊 冰山之上 (表象技能與經驗)：**\n\n{data['iceberg_analysis']['surface_skills']}")
                with ice2:
                    st.warning(f"**🧊 冰山之下 (潛在內驅力與素養)：**\n\n{data['iceberg_analysis']['deep_potential']}")

                st.markdown("---")
                st.markdown("## ⚖️ 3. 核心優勢 vs. 潛在風險")
                adv_col, risk_col = st.columns(2)
                with adv_col:
                    st.success("### ✅ 核心優勢 (Results/Impact)")
                    for s in data['core_strengths']:
                        st.markdown(f"- {s}")
                with risk_col:
                    st.error("### 🚩 潛在風險 (Red Flags)")
                    for r in data['red_flags']:
                        st.markdown(f"- {r}")

                st.markdown("---")
                st.markdown("## 🎯 4. 高階 STAR 面試攻防題庫")
                st.caption("💡 *大師心法：不問結論，問過程；問挫折，看底層態度與靈活性。*")
                for idx, q in enumerate(data['star_questions'], 1):
                    with st.expander(f"📌 題目 {idx}：針對【{q['scenario']}】"):
                        st.markdown(f"**🗣️ 靈魂拷問：** {q['question']}")
                        st.markdown(f"**👁️ 考官觀察重點 (業績=態度×能力)：** {q['what_to_look_for']}")
                        
            except Exception as e:
                st.error(f"分析過程出現錯誤：{str(e)}")
