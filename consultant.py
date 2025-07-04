import os
from datetime import datetime

import jwt
from flask import Blueprint, request
from flask_socketio import join_room, emit

from exts import socketio, db
from models import MessageModel, PatientModel



@socketio.on('connect')
def connect():
    print("Client connected")

@socketio.on('disconnect')
def disconnect():
    print("disconnected")

@socketio.on('sendMessage')
def message(data):
    from_user = data['from_user']
    from_user_avatar = data['from_user_avatar']
    to_user = data['to_user']
    to_user_avatar = data['to_user_avatar']
    content = data['content']
    print(content)
    read = 0
    type = data['type']
    try:
        message = MessageModel(from_user=from_user, from_user_avatar=from_user_avatar, to_user=to_user, to_user_avatar=to_user_avatar, content=content, read=read, type=type)
        db.session.add(message)
        db.session.commit()
        emit('newMessage', message.to_dict(), broadcast=True)
    except Exception as e:
        print("Error saving message:", e)
        db.session.rollback()

@socketio.on("joinRoom")
def joinRoom(data):
    doctorId = data['doctorId']
    emit('newRoom', {'doctorId': doctorId}, broadcast=True)

@socketio.on('leaveRoom')
def leaveRoom(data):
    doctorId = data['doctorId']
    patientId = data['patientId']
    patientName = data['patientName']
    emit('endConsultation', {'doctorId': doctorId, 'patientId': patientId, 'patientName': patientName}, broadcast=True)



