import streamlit as st
import requests

# 直接写死API Key
api_key = st.secrets["DEEPSEEK_KEY"]

# 频率限制
if "gen_count" not in st.session_state:
    st.session_state.gen_count = 0

# 页面标题
st.title("📝 小红书文案生成器")

# 检查Key是否存在
if not api_key:
    st.error("⚠️ 服务暂不可用，请联系管理员")
    st.stop()

# 主界面
topic = st.text_input("你想写什么内容？")
style = st.selectbox("文案风格", ["温柔治愈", "搞笑幽默", "干货分享", "情感共鸣", "测评推荐", "避雷吐槽", "穿搭分享", "教程攻略", "美食分享", "健身塑形", "伤心抑郁"])

if st.button("一键生成文案"):
    if st.session_state.gen_count >= 10:
        st.error("今日免费次数已用完，明天再来吧~")
    elif not topic:
        st.error("请输入内容")
    else:
        with st.spinner("正在写文案..."):
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
                        
                        st.success("生成成功！")
                        st.markdown("---")
                        st.markdown(output)
                        st.code(output, language="markdown")
                        
                        # 只有真正生成成功，才增加次数
                        st.session_state.gen_count += 1
                        
            except requests.exceptions.Timeout:
                st.error("生成超时：API响应太慢，请稍后重试")
            except requests.exceptions.ConnectionError:
                st.error("网络连接失败：请检查网络后重试")
            except Exception as e:
                st.error(f"生成失败：{str(e)}")
