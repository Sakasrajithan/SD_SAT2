from flask import Flask, request, jsonify

app = Flask(__name__)

ambulances = {1: {"available": True, "latitude": 11.017,
                  "longitude": 76.956}}
requests_db = {}

@app.route('/api/emergencies', methods=['POST'])
def create():
    rid = len(requests_db) + 501
    aid = next((i for i, a in ambulances.items()
                if a["available"]), None)
    data = request.get_json()

    requests_db[rid] = {
        "status": "ASSIGNED" if aid else "SEARCHING",
        "ambulanceId": aid,
        "latitude": data["latitude"],
        "longitude": data["longitude"]
    }
    if aid:
        ambulances[aid]["available"] = False

    return jsonify({"requestId": rid, **requests_db[rid]}), 201

@app.route('/api/ambulances/<int:aid>', methods=['GET'])
def details(aid):
    return jsonify(ambulances.get(aid, {"error": "Not found"}))

@app.route('/api/ambulances/<int:aid>/location', methods=['GET'])
def location(aid):
    a = ambulances.get(aid)
    return jsonify({"latitude": a["latitude"],
                    "longitude": a["longitude"]}) if a else (
        jsonify({"error": "Not found"}), 404)

@app.route('/api/emergencies/<int:rid>/status', methods=['GET'])
def status(rid):
    e = requests_db.get(rid)
    return (jsonify(e), 200) if e else (
        jsonify({"error": "Not found"}), 404)

@app.route('/api/emergencies/<int:rid>/cancel', methods=['PATCH'])
def cancel(rid):
    e = requests_db.get(rid)
    if not e:
        return jsonify({"error": "Not found"}), 404
    e["status"] = "CANCELLED"
    aid = e.get("ambulanceId")
    if aid:
        ambulances[aid]["available"] = True
    return jsonify(e), 200
@app.route('/')
def home():
    return jsonify({
        "message": "Emergency Ambulance Dispatch Platform",
        "status": "Running",
        "apis": [
            "/api/emergencies",
            "/api/ambulances/1",
            "/api/ambulances/1/location",
            "/api/emergencies/501/status"
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)