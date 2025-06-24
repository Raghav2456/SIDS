from flask import Flask, Response, render_template_string
import time
import random
import threading
import queue
from datetime import datetime

app = Flask(__name__)
alerts_queue = queue.Queue()

alerts_list = [
    "Multiple failed login attempts detected.",
    "Suspicious activity on port 22.",
    "High traffic volume from unknown IP.",
    "Unauthorized file access attempt.",
    "Potential malware signature found."
]

def detection_simulator():
    while True:
        time.sleep(random.randint(3, 7))
        alert = random.choice(alerts_list)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("✅ Generating alert:", f"{timestamp} - {alert}")  # 👈 ADD THIS LINE
        alerts_queue.put(f"{timestamp} - {alert}")


@app.route('/stream')
def stream():
    def event_stream():
        while True:
            alert = alerts_queue.get()
            yield f"data: {alert}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

RAW_HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Smart IDS Real-Time Alerts</title>
    <style>
        body [[ font-family: Arial, sans-serif; margin: 40px; background: #222; color: #eee; ]]
        h1 [[ color: #0f0; ]]
        #alerts [[ margin-top: 20px; ]]
        .alert [[ background: #333; margin-bottom: 10px; padding: 10px; border-left: 5px solid #0f0; ]]
    </style>
</head>
<body>
    <h1>🛡️ Smart Intrusion Detection System</h1>
    <div id="alerts"></div>
    <script>
        const alertsDiv = document.getElementById('alerts');
        const evtSource = new EventSource("/stream");
        evtSource.onmessage = function(e) {
            const newAlert = document.createElement('div');
            newAlert.className = 'alert';
            newAlert.textContent = e.data;
            alertsDiv.prepend(newAlert);
        };
    </script>
</body>
</html>"""

@app.route('/')
def index():
    html = RAW_HTML_PAGE.replace('[[', '{').replace(']]', '}')
    return render_template_string(html)

if __name__ == '__main__':
    threading.Thread(target=detection_simulator, daemon=True).start()
    app.run(debug=False, threaded=True)
