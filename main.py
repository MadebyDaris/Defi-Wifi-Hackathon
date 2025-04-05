from flask import Flask, jsonify
import Scanner

app = Flask(__name__)

@app.route("/scan", methods=["GET"])
def scan_endpoint():
    data = Scanner.scan_with_metadata()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)