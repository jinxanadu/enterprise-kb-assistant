import streamlit as st
import requests
from typing import Optional

API_BASE = "http://127.0.0.1:8002"

st.set_page_config(page_title="企业知识库助手", layout="wide")

# 页面标题
st.title("📚 企业知识库智能助手")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# 左侧边栏：文档管理
# ======================
with st.sidebar:
    st.header("📁 文档管理")

    # 上传文件
    uploaded_file = st.file_uploader("上传文档", type=["pdf", "txt", "docx", "md"])
    visibility = st.selectbox("可见性", options=["公开", "内部", "机密"], index=0)
    # 将中文选项映射回后端需要的英文值
    visibility_map = {"公开": "public", "内部": "internal", "机密": "confidential"}
    doc_id = st.text_input("文档ID（可选）", help="用于细粒度访问控制")

    if st.button("📤 上传并解析文档"):
        if uploaded_file is None:
            st.error("请先选择一个文件上传。")
        else:
            with st.spinner("正在上传并处理文档……"):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"visibility": visibility_map[visibility]}
                if doc_id.strip():
                    data["doc_id"] = doc_id.strip()

                try:
                    response = requests.post(f"{API_BASE}/ingest", files=files, data=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ 上传成功！已保存为：`{result['saved_as']}`\n\n共生成 {result['chunks']} 个文本块")
                    else:
                        st.error(f"❌ 失败：{response.json().get('detail', '未知错误')}")
                except Exception as e:
                    st.error(f"⚠️ 请求失败：{str(e)}")

    st.divider()

    # 重新索引
    st.subheader("🔄 重建知识库索引")
    reindex_visibility_label = st.selectbox("所有文档默认可见性", ["公开", "内部", "机密"], index=0)
    reindex_visibility = visibility_map[reindex_visibility_label]

    if st.button("🔥 重新索引全部文档"):
        with st.spinner("正在重建知识库索引……此过程可能需要几分钟。"):
            try:
                response = requests.post(f"{API_BASE}/reindex", data={"visibility_default": reindex_visibility})
                if response.status_code == 200:
                    res = response.json()
                    st.success(f"✅ 重建完成！共处理 {res['docs']} 个文档，生成 {res['chunks']} 个文本块")
                else:
                    st.error(f"❌ 重建失败：{response.json().get('detail', '未知错误')}")
            except Exception as e:
                st.error(f"⚠️ 请求失败：{str(e)}")

    st.divider()
    st.caption("后端服务：FastAPI + ChromaDB")

# ======================
# 主聊天区域
# ======================
st.subheader("💬 提出你的问题")

# 显示聊天历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入
if prompt := st.chat_input("在这里输入你的问题……"):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用后端 /chat 接口
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 正在思考中……")

        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={
                    "text": prompt,
                    "user_role": "public",  # 实际项目中可根据用户身份动态设置
                    "requester": "streamlit_user"
                }
            )
            if response.status_code == 200:
                answer = response.json()["answer"]
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                err_detail = response.json().get("detail", "未知错误")
                message_placeholder.markdown(f"❌ 错误：{err_detail}")
                st.session_state.messages.append({"role": "assistant", "content": f"错误：{err_detail}"})
        except Exception as e:
            error_msg = f"⚠️ 无法连接到后端服务：{str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 快捷问题示例（可选）
with st.expander("💡 示例问题"):
    st.write("- 公司关于远程办公的政策是什么？")
    st.write("- 请总结第三季度财务报告。")
    st.write("- 如何申请年假？")