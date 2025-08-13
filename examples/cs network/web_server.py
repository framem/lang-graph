#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from langchain_core.messages import HumanMessage
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat import create_workflow

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs-network-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the LangGraph workflow
workflow_app = create_workflow()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'type': 'system', 'content': '🤖 CS Network Assistant gestartet! Verfügbare Bereiche: Product, Jira, Confluence, Status'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('chat_message')
def handle_chat_message(data):
    user_message = data['message']
    print(f'Received: {user_message}')
    
    try:
        # Process through LangGraph
        input_message = {
            "messages": [HumanMessage(content=user_message)]
        }
        
        result = workflow_app.invoke(input_message)
        
        # Extract AI response
        ai_response = ""
        for msg in result["messages"]:
            if msg.type == "ai":
                ai_response = msg.content
                break
        
        if not ai_response:
            ai_response = "Entschuldigung, ich konnte keine Antwort generieren."
            
        emit('message', {'type': 'bot', 'content': ai_response})
        
    except Exception as e:
        print(f'Error processing message: {e}')
        emit('message', {'type': 'bot', 'content': f'❌ Fehler beim Verarbeiten Ihrer Nachricht: {str(e)}'})

if __name__ == '__main__':
    print("🚀 CS Network Web Interface startet...")
    print("Öffnen Sie http://localhost:5000 in Ihrem Browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)