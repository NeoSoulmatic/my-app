from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from datetime import datetime, timezone

app = Flask(__name__)

# Automatically exposes /metrics endpoint for Prometheus scraping
metrics = PrometheusMetrics(app)

# Static info metric — useful for tracking app version in Grafana
metrics.info("app_info", "Application info", version="1.0.0")


@app.route("/health")
def health():
    """Liveness probe endpoint — Kubernetes will call this to check if app is alive."""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready")
def ready():
    """Readiness probe endpoint — Kubernetes calls this before sending traffic."""
    return jsonify({"status": "ready"}), 200


@app.route("/")
def hello():
    """Hello world endpoint."""
    return jsonify({
        "message": "Hello, World!",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@app.route("/info")
def info():
    """Returns some app metadata — useful for verifying deployments."""
    return jsonify({
        "app": "my-sre-app",
        "version": "1.0.0",
        "environment": "local"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
