from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
import os
from utils import Result
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('ai', __name__, url_prefix='/ai')

trimmer = trim_messages(strategy="last", max_tokens=65, token_counter=len)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个医术精湛的医生，擅长中医和西医，能够回答关于健康和疾病的各种问题，并且了解各个中山大学附属医院的详细信息。你的回答采用markdown格式。",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_base=os.getenv('OPENAI_API_BASE'),
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

chain_with_trimming = (
        RunnablePassthrough.assign(chat_history=itemgetter("chat_history") | trimmer)
        | prompt
        | model
)


def answer(input_text, session_id):
    chat_message_history = SQLChatMessageHistory(
        session_id=session_id, connection=os.getenv('DEV_DB_URI')
    )

    chain_with_message_history = RunnableWithMessageHistory(
        chain_with_trimming,
        lambda session_id: chat_message_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    response = chain_with_message_history.invoke(
        {"input": input_text},
        {"configurable": {"session_id": session_id}},
    )

    return response.content


@bp.route("", methods=['POST'])
@jwt_required()
def get_answer():
    data = request.get_json()
    input_text = data["input"]
    session_id = str(get_jwt_identity())
    ai_message = answer(input_text, session_id)
    return Result.success({"ai_message": ai_message}).to_dict()


@bp.route("", methods=['GET'])
@jwt_required()
def get_history():
    session_id = str(get_jwt_identity())
    chat_message_history = SQLChatMessageHistory(
        session_id=session_id, connection=os.getenv('DEV_DB_URI')
    )
    # 获取历史消息
    messages = chat_message_history.messages
    message_list = []
    for message in messages:
        message_list.append({
            "role": type(message).__name__,
            "content": message.content,
        })
        print(f"{type(message).__name__}: {message.content}")
    return Result.success(message_list).to_dict()

@bp.route("", methods=['DELETE'])
@jwt_required()
def clear_history():
    session_id = str(get_jwt_identity())
    chat_message_history = SQLChatMessageHistory(
        session_id=session_id, connection=os.getenv('DEV_DB_URI')
    )
    chat_message_history.clear()
    return Result.success().to_dict()
