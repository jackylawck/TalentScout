# 從 Streamlit Secrets 讀取 Token，如果 Secrets 沒有，才顯示輸入框
if "GITHUB_TOKEN" in st.secrets:
    api_key = st.secrets["GITHUB_TOKEN"]
    with st.sidebar:
        st.success("✅ GitHub Token 已從 Secrets 安全載入")
else:
    with st.sidebar:
        st.header("⚙️ 系統設定 (BYOK)")
        api_key = st.text_input(
            "輸入 GitHub Personal Access Token", 
            type="password"  # 確保預設為遮蔽狀態
        )
