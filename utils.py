# utils.py
import math
import re
import streamlit as st
from domain_map import INDUSTRY_DOMAIN_MAP, ALIAS_MAP

def normalize_text_with_aliases(text):
    normalized_text = text
    for alias, full_name in sorted(ALIAS_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if re.match(r'^[A-Za-z0-9_]+$', alias):
            normalized_text = re.sub(rf'(?i)\b{re.escape(alias)}\b', full_name, normalized_text)
        else:
            normalized_text = normalized_text.replace(alias, full_name)
    return normalized_text

@st.cache_data
def get_scored_industries(text):
    norm_text = normalize_text_with_aliases(text).lower()
    results = []
    
    for industry_name, data in INDUSTRY_DOMAIN_MAP.items():
        matched_terms = set()
        score = 0.0
        
        core_terms = data.get("core_skills", []) + data.get("major_employers", [])
        secondary_terms = data.get("public_bodies", [])
        
        for term in core_terms:
            term_lower = term.lower()
            count = norm_text.count(term_lower)
            if count > 0:
                matched_terms.add(term)
                score += (1 + math.log(count)) * 2.0 
                
        for term in secondary_terms:
            term_lower = term.lower()
            count = norm_text.count(term_lower)
            if count > 0:
                matched_terms.add(term)
                score += (1 + math.log(count)) * 1.0
                
        if score > 3.0:
            results.append({
                "industry": industry_name,
                "score": round(score, 2),
                "matched_terms": list(matched_terms),
                "data": data
            })
            
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:2]

def build_dynamic_industry_context(scored_industries):
    """基於產業矩陣，動態生成強制聯動規則與除錯日誌"""
    if not scored_industries:
        return "無特定產業傾向，請根據通用高階企業標準進行評估。", []
        
    debug_logs = []
    context = "### 香港在地化動態產業關聯矩陣 (Dynamic Industry Matrix)\n"
    context += "根據 JD 與 CV 的交集運算，此候選人強烈涉及以下產業生態圈。請嚴格應用以下強制指令進行評估：\n\n"
    
    for item in scored_industries:
        name = item["industry"]
        data = item["data"]
        context += f"**核心板塊：{name}** (矩陣匹配權重: {item['score']})\n"
        
        if data.get('major_employers'):
            context += f"- 🎯 核心雇主名單（出現即視為高度匹配）：{', '.join(data['major_employers'])}\n"
            
        # 動態提取矩陣關係
        linked_sectors = data.get('upstream_downstream', [])
        inbound = data.get('common_pathways', {}).get('inbound', [])
        outbound = data.get('common_pathways', {}).get('outbound', [])
        
        context += f"- 🔄 **動態交集指令 (Cross-Synergy Override)**：該板塊與『{', '.join(linked_sectors)}』具備高度業務重疊。若候選人具備『{', '.join(inbound)}』背景，必須視為強大的人才流入優勢；其能力亦可完美轉移至『{', '.join(outbound)}』。嚴禁將這些高價值跨界履歷判斷為「缺乏行業經驗」。\n\n"
        
        debug_logs.append({
            "industry": name,
            "score": item["score"],
            "matched_terms": item["matched_terms"],
            "dynamic_rule": f"聯動生態: {', '.join(linked_sectors)} | 人才流入: {', '.join(inbound)} | 賦能轉出: {', '.join(outbound)}"
        })
        
    return context, debug_logs
