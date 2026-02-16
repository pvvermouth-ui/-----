import streamlit as st

# ページ設定
st.set_page_config(page_title="論文検索プロンプト生成", page_icon="📄")

# --- カスタムCSSで文字サイズを調整 ---
# --- カスタムCSSで文字サイズを確実に調整 ---
st.markdown("""
    <style>
    /* 1. タイトル (h1) のサイズを強制的に小さくする */
    h1 {
        font-size: 1.5rem !important;  /* さらに小さく 1.5rem に設定 */
        padding-top: 1.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* 2. サブヘッダー (h3) のサイズ */
    h3 {
        font-size: 1.1rem !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* 3. 全体の余白（トップ）を詰めて画面を広く使う */
    .block-container {
        padding-top: 1.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("論文検索プロンプト作成")

# 入力セクション
with st.container():
    
    # --- 検索対象期間のセクション ---
    st.subheader("📅 検索対象期間")

    # 1. 制限なしのチェックボックス
    no_limit = st.checkbox("期間制限なし（全期間を対象にする）", value=False)

    # 2. 1年〜20年のスライダー
    # チェックが入っている場合は disabled=True になり、操作できなくなります
    period_years = st.select_slider(
        "検索対象（年）",
        options=list(range(1, 21)),
        value=5,
        disabled=no_limit,
        help="チェックボックスがオフの時に有効です"
    )

    # プロンプト用の期間テキストを決定
    if no_limit:
        period_text = "制限なし（全期間）"
    else:
        period_text = f"過去 {period_years} 年以内"

    # --- プロンプト生成ロジック内の変更 ---
    # 以前の full_prompt = f""" ... の中の「期間: {period}」を
    # 「期間: {period_text}」に書き換えてください。

    st.subheader("👤 対象者（P）の情報")
    p_disease = st.text_input("疾患名", placeholder="例：脳卒中、大腿骨近位部骨折")
    p_symptom = st.text_input("主な症状", 
                           placeholder="例：弛緩性麻痺、歩行時の立脚後期での膝折れ")
    p_severity = st.text_input("重症度（任意）", placeholder="例：SIAS 30点、自立歩行困難、Br.stage III")

    st.subheader("💡 介入（I）・アウトカム（O）")
    i_input = st.text_input("介入 (任意): 具体的な技術（空欄で最新トレンド検索）", 
                          placeholder="例：装具療法、ロボットリハ、促通反復療法")
    
    o_input = st.text_input("アウトカム (任意): 改善したい指標（空欄で機能改善、ADL向上）", 
                          placeholder="例：歩行速度、ADL(FIM)、麻痺側使用頻度")

    st.subheader("🔑 自由キーワード")
    free_keywords = st.text_input("キーワード", 
                                placeholder="例：USN、二重課題、バイオメカニクス")
    exclude_keywords = st.text_input("除外したいキーワード", 
                                placeholder="例：ロボット")

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
- **介入 (I)**: {i_input if i_input else "特定の指定なし（最新のトレンドおよび、この症例に特有の課題に対する介入を優先しつつ幅広い視点や方向性で）"}
- **期待する結果 (O)**: {o_input if o_input else "機能改善、ADL向上"}
- **重要視するキーワード**: {free_keywords if free_keywords else "なし"}
- **以下の内容は提案から完全に除外してください**：{exclude_keywords if exclude_keywords else "なし"}

# 厳守事項（ハルシネーション防止）
1. 著者名、論文タイトル、URLは、Google検索の結果と100%一致するもののみを出力してください。
2. 存在しないURLを「生成」することは厳禁です。リンクが見つからない場合は「リンクなし」と記載してください。

# 検索のこだわり
- 期間: {period_text}
- 言語: 日本語および英語（英語論文は日本語で解説すること）
- 情報源: PubMed, Cochrane Library, Google Scholar, PEDro等
- 論文の種類: RCT、メタ分析、システマティックレビュー、または信頼性の高い症例報告

# 出力形式
1. **タイトル（原題）**
2. **タイトル（和訳）**
3. **要約（PICO形式で）**
4. **臨床的意義**: 介入の頻度・強度・期間の目安や、現場での具体的な活用法
5. **著者と年**
6. **エビデンスレベル**
7. **URL**

# 制約事項
- 存在しない架空の論文を絶対に生成しないでください。
- 専門用語はリハビリ職が理解できる適切な用語を使用してください。
- 回答を出力する直前に、自分自身で「このURLは本当に正しいか？」「この著者は実在するか？」を再確認し、修正した上で出力してください。"""

        st.success("プロンプトが完成しました！")

        # 1. 【共通】コピーボタン（これは全デバイス共通で動作します）
        copy_html = f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <button id="copy-btn" style="
                    background-color: #f0f2f6; color: #31333f; border: 1px solid #dcdfe6;
                    padding: 15px; font-size: 1.1rem; border-radius: 12px; width: 100%; font-weight: bold;
                ">プロンプトをコピーする</button>
            </div>
            <script>
            document.getElementById('copy-btn').addEventListener('click', function() {{
                const text = `{full_prompt.replace("`", "\\`").replace("${", "\\${")}`;
                navigator.clipboard.writeText(text).then(() => {{
                    this.innerText = '✅ コピー完了！';
                    this.style.backgroundColor = '#e1ff8d';
                }});
            }});
            </script>
        """
        st.components.v1.html(copy_html, height=80)

        # 2. 【デバイス判定 & ボタン出し分け】
        gemini_url = "https://gemini.google.com/app"

        # デバイスごとの最適なリンク形式をJavaScriptで動的に生成
        device_switch_html = f"""
        <div id="button-container" style="text-align: center;"></div>
        <script>
        const container = document.getElementById('button-container');
        const ua = navigator.userAgent.toLowerCase();
        const url = "{gemini_url}";

        if (ua.indexOf('android') > -1) {{
            // --- Android用: PWAでもブラウザでも「intent」リンクが最強 ---
            // これでPlayストアに飛ぶ場合は、長押しを推奨するテキストを添える
            container.innerHTML = `
                <a href="intent://gemini.google.com/app#Intent;package=com.google.android.apps.bard;scheme=https;end;" 
                   style="display:block; background:#1a73e8; color:white; padding:15px; border-radius:12px; text-decoration:none; font-weight:bold;">
                   Geminiアプリを起動 (Android)
                </a>
                <p style="font-size:0.8rem; color:gray; margin-top:5px;">※開かない場合はボタンを長押ししてください</p>
            `;
        }} else if (ua.indexOf('iphone') > -1 || ua.indexOf('ipad') > -1) {{
            // --- iOS用: 通常リンクがユニバーサルリンクとして機能 ---
            container.innerHTML = `
                <a href="${{url}}" target="_blank" 
                   style="display:block; background:#1a73e8; color:white; padding:15px; border-radius:12px; text-decoration:none; font-weight:bold;">
                   Geminiを起動 (iOS)
                </a>
            `;
        }} else {{
            // --- Windows/PC用: window.open で別窓ポップアップ ---
            container.innerHTML = `
                <button onclick="window.open('${{url}}', '_blank', 'width=1000,height=800');"
                   style="display:block; width:100%; background:#1a73e8; color:white; padding:15px; border-radius:12px; border:none; font-weight:bold; cursor:pointer;">
                   Geminiを別画面で起動 (PC)
                </button>
            `;
        }}
        </script>
        """
        st.components.v1.html(device_switch_html, height=120)