from flask import Flask, request, render_template, send_file, redirect, url_for
import ifcopenshell
import ifcopenshell.util.element as Element
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "ifc_file" not in request.files:
        return "No file part", 400

    file = request.files["ifc_file"]
    if file.filename == "":
        return "No selected file", 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    ifc_model = ifcopenshell.open(file_path)

    extracted_data = {}
    elements = ifc_model.by_type("IfcElement")

    for element in elements:
        element_id = element.GlobalId
        extracted_data[element_id] = {
            "Type": element.is_a(),
            "Name": element.Name,
            "Properties": Element.get_psets(element)
        }

    json_path = os.path.join(DOWNLOAD_FOLDER, "extracted_data.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)

    return redirect(url_for("download_file"))

@app.route("/download")
def download_file():
    json_path = os.path.join(DOWNLOAD_FOLDER, "extracted_data.json")
    if os.path.exists(json_path):
        return send_file(json_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)