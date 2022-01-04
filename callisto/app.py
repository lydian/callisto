import os
import base64

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import Response
from flask import abort
from werkzeug.exceptions import HTTPException


from callisto.core.contents_loader import Loader
from callisto.core.config_loader import Config


app = Flask(__name__, static_folder="./built/static", template_folder="./built")

def configure_app(config):
    global app
    print("configure_app", config)
    app.callisto_config = Config.load_from_config_file(config)
    app.contents_loader = Loader(app.callisto_config)
    return app


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/<path:path>")
def index_2(path: str) -> str:
    return render_template("index.html")


@app.route("/api/info/<path:path>")
def info(path):
    if path == "<root>":
        path = ""
    return jsonify(app.contents_loader.info(path))


@app.route("/api/get/<path:path>")
def list(path: str) -> str:
    if path == "<root>":
        path = "/"
    r = app.contents_loader.get(path)
    if r["type"] == "directory":
        r["content"] = sorted(
            r["content"], key=lambda item: (item["type"] != "directory", item["name"])
        )
    return jsonify(r)


@app.route("/api/raw/<path:path>")
def raw(path):
    content = app.contents_loader.get(path, type="file")
    if content["format"] == "base64":
        content["content"] = base64.decodebytes(content["content"].encode("ascii"))
    download = bool(request.args.get("download"))
    kwargs = (
        {"headers": {"Content-Disposition": f"attachment;filename={content['name']}"}}
        if download
        else {}
    )
    return Response(content["content"], mimetype=content["mimetype"], **kwargs)


@app.route("/api/notebook/toc/<path:path>")
def toc(path):
    nb = app.contents_loader.get_nb(path)
    return jsonify(nb.toc())


@app.route("/api/notebook/render/<path:path>")
def render_nb(path):
    nb = app.contents_loader.get_nb(path)
    return nb.html_content


@app.route("/api/notebook/import/<path:path>")
def import_nb(path):
    print(path)
    path_func = getattr(app.callisto_config, "import_link_func")
    if path_func:
        path = path_func(path)

    base_url = getattr(app.callisto_config, "jupyterhub_base_url", "").rstrip("/")
    if not base_url:
        return ""

    if getattr(app.callisto_config, "import_link_with_hubshare_preview"):
        return (
            base_url
            + "/user-redirect/?hubshare-preview="
            + base64.b64encode(path.encode("utf-8")).decode("utf-8")
        )

    return base_url + "/user-redirect/lab/tree" + path


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    output = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description
    })
    response.content_type = "application/json"
    return output, e.code
