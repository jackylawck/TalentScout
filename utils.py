# utils.py
import math
import re
import streamlit as st
from domain_map import INDUSTRY_DOMAIN_MAP, ALIAS_MAP

def normalize_text_with_aliases(text):
    """處理中英夾雜與別名，統一替換為標準全稱"""
    normalized_text = text
    # 依長度排序避免部分替換錯誤
    for alias, full_name in sorted(ALIAS_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        # 英文縮寫使用 word boundary，中文直接替換
        if re.match(r'^[A-Za-z0-9_]+$', alias):
            normalized_text = re.sub(rf'(?i)\b{re.escape(alias)}\b', full_name, normalized_text)
        else:
            normalized_text = normalized_text.replace(alias, full_name)
    return normalized_text

@st.cache_data
def get_scored_industries(text):
    """計算產業關聯分數 (採用 Log-TF 詞頻平滑加權)"""
    norm_text = normalize_text_with_aliases(text).lower()
    results = []
    
    for industry_name, data in INDUSTRY_DOMAIN_MAP.items():
        matched_terms = set()
        score = 0.0
        
        # 賦予核心關鍵字較高權重
        core_terms = data.get("core_keywords", []) + data.get("major_employers", [])
        secondary_terms = data.get("skill_tags", []) + data.get("public_bodies", [])
        
        # 計算核心權重 (Multiplier: 2.0)
        for term in core_terms:
            term_lower = term.lower()
            count = norm_text.count(term_lower)
            if count > 0:
                matched_terms.add(term)
                score += (1 + math.log(count)) * 2.0 
                
        # 計算次要權重 (Multiplier: 1.0)
        for term in secondary_terms:
            term_lower = term.lower()
            count = norm_text.count(term_lower)
            if count > 0:
                matched_terms.add(term)
                score += (1 + math.log(count)) * 1.0
                
        # 設定最低相關性門檻 (Threshold)
        if score > 3.0:
            results.append({
                "industry": industry_name,
                "score": round(score, 2),
                "matched_terms": list(matched_terms),
                "data": data
            })
            
    # 依分數遞減排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # 只回傳 Top 2 高相關板塊，避免 Context 過長
    return results[:2]

def build_dynamic_industry_context(scored_industries):
    """生成注入給 LLM 的輕量化產業摘要"""
    if not scored_industries:
        return "無特定產業傾向，請根據通用高階企業標準進行評估。"
        
    context = "### 香港在地化產業關聯指南 (Localized Industry Context)\n"
    context += "根據 JD 與 CV 內容，此候選人強烈涉及以下產業生態圈。請在評估時，將以下「主要僱主」的經歷視為高度相關的行業優勢（Industry Match）：\n\n"
    
    for item in scored_industries:
        name = item["industry"]
        data = item["data"]
        context += f"**板塊：{name}** (關聯權重分數: {item['score']})\n"
        context += f"- 關鍵技能雷達：{', '.join(data.get('skill_tags', []))}\n"
        context += f"- 視為高度關聯的主要僱主：{', '.join(data.get('major_employers', []))}\n\n"
        
    return context
