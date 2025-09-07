import openai
import streamlit as st
from openai import OpenAI
import os
import time

# 페이지 설정
st.set_page_config(
    page_title="🌍 여행 챗봇",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일
st.markdown("""
<style>
    /* 메인 컨테이너 스타일 */
    .main {
        padding-top: 2rem;
    }
    
    /* 제목 스타일 */
    .main-title {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 사이드바 스타일 */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 채팅 컨테이너 */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 사용자 메시지 스타일 */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        animation: slideInRight 0.3s ease-out;
    }
    
    /* 봇 메시지 스타일 */
    .bot-message {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        animation: slideInLeft 0.3s ease-out;
    }
    
    /* 시스템 메시지 숨기기 */
    .system-message {
        display: none;
    }
    
    /* 애니메이션 */
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* 입력 박스 스타일 */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* 경고 메시지 스타일 */
    .warning-box {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        margin: 1rem 0;
    }
    
    /* 로딩 애니메이션 */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# 메인 제목
st.markdown('<h1 class="main-title">🌍 여행 전문 AI 챗봇 ✈️</h1>', unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    st.markdown("---")
    
    openai_api_key = st.text_input(
        "🔑 OpenAI API 키", 
        type="password",
        help="OpenAI API 키를 입력해주세요"
    )
    
    st.markdown("---")
    st.markdown("### 📋 사용 가이드")
    st.markdown("""
    - 🗺️ **여행지 추천** 문의
    - 🎒 **준비물** 안내
    - 🍜 **현지 음식** 정보
    - 🏛️ **문화** 및 **관광지** 소개
    - 💡 **여행 팁** 제공
    """)
    
    st.markdown("---")
    st.markdown("### 🚨 주의사항")
    st.markdown("""
    - 여행 관련 질문만 답변합니다
    - 정확한 정보 제공을 위해 노력합니다
    - 불확실한 내용은 명시합니다
    """)

# API 키 확인
if not openai_api_key:
    st.markdown("""
    <div class="warning-box">
        <h3>⚠️ API 키가 필요합니다</h3>
        <p>왼쪽 사이드바에서 OpenAI API 키를 입력해주세요.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=openai_api_key)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [  
        {"role": "system", 
         "content": "기본적으로 한국어와 영어로 제공해 주세요. "
                   "당신은 여행에 관한 질문에 답하는 전문 챗봇입니다. "
                   "만약에 여행 외의 질문에 대해서는 정중하게 거절하고 여행 관련 질문을 유도해주세요. "
                   "확실하지 않은 내용은 추측하지 말고 정확히 모른다고 말해주세요. "
                   "여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하고 상세하게 안내해주세요."
        }  
    ]

if "loading" not in st.session_state:
    st.session_state.loading = False

# 메인 컨테이너
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # 사용자 입력
    st.markdown("### 💬 메시지를 입력하세요")
    
    # 입력 폼
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "", 
            placeholder="여행에 관해 무엇이든 물어보세요! 예: '일본 도쿄 3박4일 여행 계획을 세워주세요'",
            key="user_input"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            submit_button = st.form_submit_button("✈️ 전송", use_container_width=True)
    
    # 메시지 처리
    if submit_button and user_input:
        st.session_state.loading = True
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 로딩 표시
        with st.spinner('🤖 답변을 생성하고 있습니다...'):
            try:
                # OpenAI API 호출
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # OpenAI 응답 추가
                response_message = response.choices[0].message.content
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_message
                })
                
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        
        st.session_state.loading = False
        st.rerun()

    # 채팅 기록 표시
    st.markdown("### 💭 대화 내역")
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    with chat_container:
        # 메시지 역순으로 표시 (최신 메시지가 아래로)
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "system":
                continue
                
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 사용자:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
            elif message["role"] == "assistant":
                st.markdown(f"""
                <div class="bot-message">
                    <strong>🤖 여행 도우미:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # 대화 초기화 버튼
    if len(st.session_state.messages) > 1:
        st.markdown("---")
        col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 1])
        with col_clear2:
            if st.button("🗑️ 대화 초기화", use_container_width=True):
                st.session_state.messages = [st.session_state.messages[0]]  # 시스템 메시지만 유지
                st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌟 여행의 모든 것을 도와드리는 AI 챗봇입니다 🌟</p>
    <p><small>Powered by OpenAI GPT-4 & Streamlit</small></p>
</div>
""", unsafe_allow_html=True)
