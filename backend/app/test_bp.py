"""
Blueprint de prueba minimalista para diagnóstico
"""
from flask import Blueprint, jsonify

test_bp = Blueprint('test', __name__)

@test_bp.route('/test-minimal')
def test_minimal():
    """Endpoint minimalista para pruebas"""
    return jsonify({"status": "ok", "message": "Endpoint de prueba funcionando"})
