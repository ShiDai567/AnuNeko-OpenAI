from flask import jsonify
from app.main import sessions
def list_sessions():
    """列出会话"""
    session_list = []
    for session_id, session_data in sessions.items():
        session_list.append({
            "id": session_data["id"],
            "model": session_data["openai_model"],
            "created_at": session_data["created_at"],
            "has_anuneko_chat": session_data["has_anuneko_chat"]
        })
    
    return jsonify({
        "sessions": session_list,
        "total": len(session_list)
    })

def delete_session(session_id: str):
    """删除会话"""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"status": "success", "message": "会话已删除"})
    else:
        return jsonify({"status": "error", "message": "会话不存在"}), 404
