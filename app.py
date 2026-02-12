import streamlit as st

# ページ設定
st.set_page_config(page_title="論文検索プロンプト生成", page_icon="📄")

st.title("論文検索プロンプト作成📄")
st.caption("AIを用いた論文検索の依頼文を作成します。")

# 入力セクション
with st.container():
    # 職種は内部で固定、期間のみ選択
    period = st.select_slider("検索対象期間", options=["制限なし", "10年以内", "5年以内"], value="5年以内")

    st.subheader("👤 対象者（P）の情報")
    p_disease = st.text_input("疾患名", placeholder="例：脳卒中、大腿骨近位部骨折")
    p_symptom = st.text_input("主な症状（高次脳機能もここに）", 
                           placeholder="例：弛緩性麻痺、歩行時の立脚後期での膝折れ左、半側空間無視")
    p_severity = st.text_input("重症度（任意）", placeholder="例：SIAS 30点、自立歩行困難、Br.stage III")

    st.subheader("💡 介入（I）・アウトカム（O）")
    i_input = st.text_input("介入 (任意): 具体的な技術（空欄で最新トレンド検索）", 
                          placeholder="例：装具療法、ロボットリハ、促通反復療法")
    
    o_input = st.text_input("アウトカム (任意): 改善したい指標（空欄で機能改善、ADL向上）", 
                          placeholder="例：歩行速度、ADL(FIM)、麻痺側使用頻度")

    st.subheader("🔑 自由キーワード（高次脳・合併症など）")
    free_keywords = st.text_input("キーワード", 
                                placeholder="例：USN、認知負荷、二重課題、糖尿病、バイオメカニクス")

# プロンプト生成
if st.button("プロンプトを生成する"):
    if not p_disease:
        st.error("「疾患名」は検索に必須です。")
    else:
        # Pの情報を統合
        p_total = f"疾患：{p_disease}、症状：{p_symptom}"
        if p_severity:
            p_total += f"、機能レベル：{p_severity}"
            
        # 介入(I)の有無によるモード切替
        if i_input:
            intent_text = f"「{i_input}」の効果と臨床適応について調査してください。"
        else:
            intent_text = "最新の推奨される治療アプローチと、そのエビデンスを網羅的に調査してください。"

        # 職種固定
        job_fixed = "理学療法"

        full_prompt = f"""あなたは{job_fixed}の臨床・研究に精通したエキスパートAIです。
以下の条件に基づき、臨床の意思決定や治療の引き出しを増やすための信頼性の高い論文を5件程度リストアップしてください。

# 調査の目的
{intent_text}

# 条件設定
- **対象 (P)**: {p_total}
- **介入 (I)**: {i_input if i_input else "特定の指定なし（最新のトレンドおよび、この症例に特有の課題に対する介入を優先）"}
- **期待する結果 (O)**: {o_input if o_input else "機能改善、ADL向上"}
- **重要視するキーワード**: {free_keywords if free_keywords else "なし"}

# 検索のこだわり
- 期間: {period}
- 言語: 日本語および英語（英語論文は日本語で解説すること）
- 情報源: PubMed, Cochrane Library, Google Scholar, PEDro等
- 論文の種類: RCT、メタ分析、システマティックレビュー、または信頼性の高い症例報告

# 出力形式
1. **タイトル（和訳）**
2. **要約（PICO形式で）**
3. **臨床的意義**: 介入の頻度・強度・期間の目安や、現場での具体的な活用法
4. **エビデンスレベルとURL/DOI**

# 制約事項
- 存在しない架空の論文を絶対に生成しないでください。
- 専門用語はリハビリ職が理解できる適切な用語を使用してください。"""

        st.success("プロンプトが完成しました！")
        st.text_area("生成されたプロンプト", full_prompt, height=500)
        st.link_button("Geminiを開いて貼り付ける", "https://gemini.google.com/app")