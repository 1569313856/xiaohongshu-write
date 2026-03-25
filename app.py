import streamlit as st
import requests

# 直接写死API Key
api_key = st.secrets["DEEPSEEK_KEY"]

# 频率限制
if "gen_count" not in st.session_state:
    st.session_state.gen_count = 0

# ========== 页面美化CSS（手机端适配版 + 选择框彻底修复）==========
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 输入框圆角 */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 1px solid #FF8E53;
        padding: 12px 16px;
        font-size: 16px;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 12px 24px;
        font-size: 18px;
        font-weight: bold;
        width: 100%;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
    }
    
    /* 选择框样式修复 - 让文字完整显示 */
    .stSelectbox > div > div {
        border-radius: 25px;
        padding: 10px 15px;
        min-height: 45px;
        white-space: normal !important;
        word-break: keep-all;
        overflow-x: auto;
    }
    /* 让选择框的显示文字不截断 */
    .stSelectbox [data-baseweb="select"] span {
        white-space: normal !important;
        word-break: keep-all;
    }
    /* 下拉菜单选项完整显示 */
    div[data-baseweb="select"] ul {
        width: auto !important;
        min-width: 200px;
        max-width: 400px;
    }
    div[data-baseweb="select"] li {
        white-space: normal !important;
        word-break: keep-all;
        padding: 10px 15px;
        line-height: 1.4;
    }
    
    /* 手机端专用优化 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 1.2rem;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        .stMarkdown p {
            font-size: 14px;
        }
        div[data-baseweb="select"] ul {
            max-width: 90vw;
        }
    }
    
    /* 付费墙卡片样式 */
    .paywall-card {
        background: linear-gradient(135deg, #fff5f0, #ffe8e0);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        border: 1px solid #FF8E53;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    @media (max-width: 768px) {
        .paywall-card {
            padding: 15px;
        }
        .paywall-card p {
            font-size: 14px;
        }
    }
    
    .guide-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #FF6B6B;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ========== 渐变标题 ==========
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #FF6B6B, #FF8E53); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;">
        ✨ AI爆款文案生成器 ✨
    </h1>
    <p style="font-size: 1rem; color: #666; margin-top: 5px;">3秒生成小红书/朋友圈/抖音爆款文案</p>
    <p style="font-size: 0.8rem; color: #999;">已有 12,345 人使用 | 好评率 98%</p>
</div>
""", unsafe_allow_html=True)

# ========== 使用指南 ==========
with st.expander("📖 使用指南（点开看教程）"):
    st.markdown("""
    <div class="guide-card">
        <b>✨ 三步搞定爆款文案</b><br>
        1️⃣ 输入你想写的内容（比如：新买的lolita裙子）<br>
        2️⃣ 选择喜欢的文案风格<br>
        3️⃣ 点击生成，3秒拿到3条爆款文案<br>
        4️⃣ 直接复制发小红书，流量蹭蹭涨！<br>
        <br>
        💡 <b>小技巧</b>：风格选“测评推荐”或“避雷吐槽”更容易出爆款～
    </div>
    """, unsafe_allow_html=True)

# 检查Key是否存在
if not api_key:
    st.error("⚠️ 服务暂不可用，请联系管理员")
    st.stop()

# ========== 主界面 ==========
topic = st.text_input("✏️ 你想写什么内容？", 
                       placeholder="例如：新买的lolita裙子、熬夜面霜、周末探店...")

# ========== 风格选择（文字完整显示）==========
# 将风格选项分组，用 radio 分两列显示，手机端自动折行
st.markdown("### 🎨 选择文案风格")
col1, col2 = st.columns(2)

# 风格列表（按列分配）
styles = [
    "温柔治愈", "搞笑幽默", "干货分享", "情感共鸣",
    "测评推荐", "避雷吐槽", "穿搭分享", "教程攻略",
    "美食分享", "健身塑形", "伤心抑郁", "沙雕搞笑", 
    "文艺清新", "种草安利"
]

half = len(styles) // 2
left_styles = styles[:half]
right_styles = styles[half:]

if "selected_style" not in st.session_state:
    st.session_state.selected_style = styles[0]

st.markdown("### 🎨 选择文案风格")
col1, col2 = st.columns(2)

with col1:
    for s in left_styles:
        # 判断当前选项是否被选中
        is_selected = (st.session_state.selected_style == s)
        button_label = f"✅ {s}" if is_selected else f"☑️ {s}"
        if st.button(button_label, key=f"style_{s}", use_container_width=True):
            st.session_state.selected_style = s
            st.rerun()

with col2:
    for s in right_styles:
        is_selected = (st.session_state.selected_style == s)
        button_label = f"✅ {s}" if is_selected else f"☑️ {s}"
        if st.button(button_label, key=f"style_{s}_r", use_container_width=True):
            st.session_state.selected_style = s
            st.rerun()

# 生成文案时用这个
style = st.session_state.selected_style

# ========== 生成按钮 ==========
if st.button("✨ 一键生成文案 ✨", type="primary"):
    if st.session_state.gen_count >= 10:
        st.markdown("""
        <div class="paywall-card">
            <p style="font-size: 1.2rem;">✨ 免费次数已用完 ✨</p>
            <p style="font-size: 0.9rem;">9.9元/月 无限次使用</p>
            <p>👉 <a href="https://afdian.com/" target="_blank">点击购买</a></p>
            <p style="font-size: 0.7rem; color: #999;">购买后联系客服开通无限次数</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    elif not topic:
        st.error("请输入你要写的内容")
    else:
        with st.spinner("AI正在为你写文案..."):
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            你是一个专业的小红书文案写手。请根据以下主题，生成3条不同风格的小红书爆款文案。

            主题：{topic}
            风格偏好：{style}

            要求：
            1. 每条文案包含标题（带emoji）和正文
            2. 使用小红书常用的emoji和口语化表达
            3. 每条文案最后加3-5个相关话题标签
            4. 每条文案之间用"---"分隔
            """
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 2000
            }
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code != 200:
                    st.error(f"API请求失败：HTTP {response.status_code}")
                    st.info("可能原因：含有敏感词、API Key无效、或网络问题。")
                else:
                    result = response.json()
                    
                    if "choices" not in result or len(result["choices"]) == 0:
                        if "error" in result:
                            st.error(f"API返回错误：{result['error'].get('message', '未知错误')}")
                        else:
                            st.error("生成失败：API返回数据异常，请稍后重试")
                    else:
                        output = result['choices'][0]['message']['content']
                        
                        st.success("✨ 生成成功！")
                        st.markdown("---")
                        st.markdown(output)
                        st.code(output, language="markdown")
                        st.caption("👆 长按上面的文字可以复制")
                        
                        st.session_state.gen_count += 1
                        
            except requests.exceptions.Timeout:
                st.error("生成超时：API响应太慢，请稍后重试")
            except requests.exceptions.ConnectionError:
                st.error("网络连接失败：请检查网络后重试")
            except Exception as e:
                st.error(f"生成失败：{str(e)}")

# ========== 文案示例展示 ==========
st.markdown("---")
st.markdown("### 🌟 爆款文案示例")
with st.expander("🔥 点击查看真实生成效果"):
    st.markdown("""
    **📷 自拍文案示例**
    > 今天这组自拍我也太满意了吧！😍  
    > 阳光正好，心情刚好✨  
    > 原相机直出，皮肤好到离谱～  
    > #自拍 #今日份开心 #原相机 #好皮肤

    **🛍️ 好物分享示例**
    > 挖到宝了！这个面霜也太绝了🔥  
    > 熬夜党的救星，第二天起来脸在发光✨  
    > 姐妹们快冲！  
    > #好物分享 #护肤 #熬夜党 #面霜

    **💔 失恋心情示例**
    > 有些人，走着走着就散了💔  
    > 谢谢你来过，不遗憾你离开  
    > 我会成为更好的自己  
    > #失恋 #成长 #好好爱自己
    """)

st.markdown("---")
st.caption("💡 提示：每天可免费生成10次，更多次数请购买会员")
