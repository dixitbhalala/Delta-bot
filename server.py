from flask import Flask, request, jsonify
from datetime import datetime
from main import execute_trade, get_position

app = Flask(__name__)

alerts_received = []


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("\n" + "=" * 60)
        print(f"🔔 ALERT RECEIVED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Raw data
        raw_data = request.get_data(as_text=True)
        print("📩 Raw Data:", raw_data)

        # Parse data
        alert_data = None

        if request.is_json:
            alert_data = request.get_json()

        elif request.form:
            alert_data = request.form.to_dict()

        elif raw_data:
            from urllib.parse import parse_qs
            parsed = parse_qs(raw_data)
            alert_data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

        if not alert_data:
            alert_data = {"raw_message": raw_data}

        print("📦 Parsed Data:", alert_data)

        # ==============================
        # 🔍 SIGNAL EXTRACTION (UPDATED)
        # ==============================
        signal = None

        # Case 1: JSON
        if isinstance(alert_data, dict):
            signal = alert_data.get("signal")

        # Case 2: Plain text (FIXED)
        if not signal and raw_data:
            raw_clean = raw_data.strip().upper()

            if raw_clean == "LONG":
                signal = "LONG"
            elif raw_clean == "SHORT":
                signal = "SHORT"

        print(f"📢 Signal Detected: {signal}")

        # ==============================
        # 🛑 VALIDATION + EXECUTION
        # ==============================
        if signal not in ["LONG", "SHORT"]:
            print("⚠️ Invalid or missing signal → skipping trade")

        else:
            current_position = get_position()
            print("📊 Current Position:", current_position)

            if current_position == signal:
                print("⚠️ Same position already exists → skipping trade")
            else:
                execute_trade(signal)

        # Store alert
        alerts_received.append({
            "timestamp": datetime.now().isoformat(),
            "signal": signal,
            "data": alert_data,
            "raw_data": raw_data
        })

        return jsonify({
            "status": "success",
            "signal": signal,
            "alerts_count": len(alerts_received)
        }), 200

    except Exception as e:
        print("❌ ERROR:", str(e))

        import traceback
        traceback.print_exc()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 200


# ==============================
# 📊 DEBUG ENDPOINTS
# ==============================

@app.route('/alerts', methods=['GET'])
def get_alerts():
    return jsonify({
        "total_alerts": len(alerts_received),
        "alerts": alerts_received
    })


@app.route('/clear', methods=['POST'])
def clear_alerts():
    alerts_received.clear()
    return jsonify({
        "status": "success",
        "message": "All alerts cleared"
    })


@app.route('/', methods=['GET'])
def home():
    return """
    <h1>Trading Bot Webhook Server</h1>
    <p>Status: Running</p>
    <p><b>POST /webhook</b> → Receive TradingView alerts</p>
    <p><b>GET /alerts</b> → View alerts</p>
    <p><b>POST /clear</b> → Clear alerts</p>
    """


# ==============================
# 🚀 RUN SERVER
# ==============================

if __name__ == '__main__':
    print("🚀 Starting Trading Bot Server...")
    print("=" * 60)
    print("🌐 Local: http://127.0.0.1:5000")
    print("🌍 Use ngrok URL in TradingView")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)