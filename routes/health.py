# routes/health.py
from flask import Blueprint, jsonify

# Blueprint: Bu dosyadaki tüm endpointler /api/health altına bağlanacak
health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Backend ayakta"
    })
