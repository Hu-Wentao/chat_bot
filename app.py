import json
from typing import Optional

from langchain.chat_models import AzureChatOpenAI
from langchain.chat_models.base import BaseChatModel
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, ChatMessage, AIMessage

from backend import prompt_by, prompt_patch, prompt_create


# ==== biz (st + function)


@st.cache_resource
def get_llm() -> BaseChatModel:
    __llm = st.secrets.get("llm")
    llm = AzureChatOpenAI(
        openai_api_base=__llm.get("OPENAI_API_BASE"),
        openai_api_key=__llm.get("OPENAI_API_KEY"),
        openai_api_version=__llm.get("OPENAI_API_VERSION"),
        deployment_name=__llm.get("DEPLOYMENT_NAME"),
        openai_api_type="azure",
    )
    return llm


def get_base_url() -> str:
    return st.secrets.get("frontend")["base_url"]


def build_url(base_url: str, sc: str, prompt_id: str, member_id: str = '') -> str:
    return f"{base_url}?screen={sc}&prompt_id={prompt_id}&member_id={member_id}"


def load_query_param():
    """读取参数, 加载到状态中
    从后端读取数据,仅限于 'not in' ,并且 'id!=""’ 时, 这代表首次进入页面, 所以才从后端读取数据.
    """
    query_params = st.experimental_get_query_params()
    if "screen" not in st.session_state:
        st.session_state.screen = query_params.get("screen", ["home"])[0]

    if "prompt_id" not in st.session_state:
        data = prompt_by(st.secrets['backend'], query_params.get("prompt_id", [""])[0])
        set_prompt(data)

    # if "member_id" not in st.session_state:
    #     data = member_by(query_params.get("member_id", [""])[0])
    #     set_member(data)
    # if "lang" not in st.session_state:
    #     st.session_state.lang = query_params.get("lang", ["en_US"])[0]


def _get_first_system(content: list[dict]) -> Optional[dict]:
    for item in content:
        # 如果角色为system'，则打印其内容并退出循环
        if item['role'] == 'system':
            return item['content']


def _set_prompt_prompt_system(data: dict):
    st.session_state.prompt_system = _get_first_system(data.get("content", []))
    pass


def _set_prompt_message(data: dict):
    """将提示词转换为对象"""
    msg = []
    for m in data.get("content", []):

        if m['role'] == 'system':
            msg.append(SystemMessage(content=m['content']))
        elif m['role'] == 'user' or m['role'] == 'human':
            msg.append(HumanMessage(content=m['content']))
        else:
            msg.append(AIMessage(content=m['content']))
    st.session_state.messages = msg
    pass


def set_prompt(_data: dict):
    """设置状态中的 prompt
    """
    data = _data or {}
    st.session_state.prompt_id = data.get("id", "")
    st.session_state.prompt_name = data.get("name", "")
    st.session_state.prompt_content = data.get("content", [])
    # 特殊处理,提取system
    _set_prompt_prompt_system(data)
    # 特殊处理,存储到message
    _set_prompt_message(data)
    pass


def submit_chat():
    """
    """
    user_input = st.session_state.user_input
    st.session_state.messages.append(HumanMessage(content=user_input))
    response: BaseMessage = get_llm().invoke(st.session_state.messages)
    st.session_state.messages.append(response)


def fragment_chat():
    # if "messages" not in st.session_state:
    #     st.session_state["messages"] = st.session_state.prompt_content
    # st.session_state["messages"]: list[BaseMessage] = [
    #     SystemMessage(content=st.session_state.prompt_system)
    # ]

    for msg in st.session_state.messages:
        if msg.type != 'system' and msg is not SystemMessage:
            with st.chat_message(msg.type):
                f"""
                {msg.content}
                """
    st.chat_input(  # f"请发送您的理由",
        key='user_input',
        # max_chars=1000,
        on_submit=submit_chat)


# === UI - logic (callback + statement)
def update_query_param():
    """更新特定的param, 其他保持原样"""
    param = {
        "screen": st.session_state.screen,
        "prompt_id": st.session_state.prompt_id,
    }
    for k, v in st.experimental_get_query_params().items():
        if k not in param:
            param[k] = v[0]
    # print("debug update_query_param#2#", param)
    st.experimental_set_query_params(**param)


def submit_prompt():
    """点击提交按钮: 创建/更新prompt"""
    content: list[dict] = st.session_state.prompt_content
    content.insert(0, {"role": "system", "content": st.session_state.prompt_system})
    if not is_prompt_check():
        record = prompt_create(bk=st.secrets['backend'],
                               name=st.session_state.prompt_name,
                               content=content,
                               )
        set_prompt(record)
        update_query_param()
    else:
        record = prompt_patch(bk=st.secrets['backend'],
                              prompt_id=st.session_state.prompt_id,
                              prompt_name=st.session_state.prompt_name,
                              prompt_content=content,
                              )
        set_prompt(record)
    pass


def is_prompt_check():
    return st.session_state.prompt_id != ""


def on_submit_prompt_msg():
    st.session_state.prompt_content.append({
        "role": st.session_state.add_role,
        "content": st.session_state.add_content,
    })
    pass


def fragment_create_prompt():
    """"prompt表单"""
    with st.form("prompt", ):
        st.text_input(
            "Bot名称",
            key='prompt_name',
            placeholder=f"李白",
            help="将会展示在聊天页标题中"
        )
        st.text_area(
            "系统提示词",
            key='prompt_system',
            placeholder="你是中国古代诗人李白",
            help="这里的内容将作为system提示词, 并且不会被展示在界面中"
        )
        btn_text = "提交提示词" if not is_prompt_check() == "" else "修改提示词"
        st.form_submit_button(btn_text, on_click=submit_prompt)
    with st.expander("高级"):
        st.session_state
        if 'prompt_content' not in st.session_state:
            st.session_state.prompt_content = []
        for i, m in zip(range(len(st.session_state.prompt_content)), st.session_state.prompt_content):
            with st.chat_message(name=m['role']):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"""{m['content']}""")
                with col2:
                    def _remove_content_msg(index: int):
                        st.session_state.prompt_content.pop(index)

                    st.button("删除", key=f'm-{i}', on_click=_remove_content_msg, kwargs={"index": i})

                pass
        with st.form('add_prompt_msg_form'):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.selectbox(
                    "选择角色",
                    ["system", "assistant", "user", ],
                    key="add_role",
                    index=1,
                )
            with col2:
                st.text_input(
                    "请输入示例对话内容",
                    value='吾乃李白, 阁下有何贵干?',
                    key='add_content',
                )
            st.form_submit_button(on_click=on_submit_prompt_msg)
    pass


def screen_chat():
    """聊天"""
    st.title(f"💬 Chatbot( {st.session_state.prompt_name} )")
    fragment_chat()


def screen_home():
    """主页"""
    """## 创建你的Bot
    """

    fragment_create_prompt()

    if is_prompt_check():
        sc = 'chat'
        dir_url = build_url(base_url=get_base_url(), sc=sc, prompt_id=st.session_state.prompt_id)
        share_url = build_url(base_url=get_base_url(), sc=sc, prompt_id=st.session_state.prompt_id)
        f"""
        > [直接进入 ( {st.session_state.prompt_name} ) ]({dir_url})
        > 
        > 复制下方邀请链接
        > 
        > ```html
        > {share_url}
        > ```
        """


# ====

# 读取 prompt
load_query_param()
# screen
_screen = st.session_state.screen
if _screen == "home":
    screen_home()
elif _screen == "chat":
    screen_chat()
# elif _screen == "discussing":
#     screen_discussing()
# elif _screen == "voting":
#     screen_voting()
else:
    st.write("ERROR: unknown screen ", _screen)
    screen_home()
