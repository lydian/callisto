import base64
import os
from typing import Optional

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import Response
from werkzeug.exceptions import HTTPException


from callisto.core.contents_loader import ContentsLoader
from callisto.core.callisto_config import CallistoConfig
from callisto.core.private_loader import PrivateLoader


app = Flask(__name__, static_folder="./built/static", template_folder="./built")


def configure_app(config: Optional[str]) -> Flask:
    global app
    app.logger.info(f"configure_app using config: {config}")
    app.callisto_config = CallistoConfig.load_from_config_file(config)
    app.contents_loader = ContentsLoader(app.callisto_config)
    app.private_loader = PrivateLoader(app.callisto_config)
    return app


@app.route("/")
@app.route("/<path:path>")
@app.route("/private/<path:path>")
def index_2(path: str = None) -> str:
    return render_template("index.html")


@app.route("/api/info/<path:path>")
def info(path):
    if path == "<root>":
        path = ""
    return jsonify(app.contents_loader.info(path))


@app.route("/api/get/<path:path>")
def list(path: str) -> Response:
    if path == "<root>":
        path = ""
    r = app.contents_loader.get(path)
    if r["type"] == "directory":
        r["content"] = sorted(
            r["content"], key=lambda item: (item["type"] != "directory", item["name"])
        )
    return jsonify(r)


@app.route("/api/private-raw/<path:path>", defaults={"private": True})
@app.route("/api/raw/<path:path>")
def raw(path, private=False):
    loader = app.private_loader if private else app.contents_loader
    content = loader.get(path, type="file")
    if content["format"] == "base64":
        content["content"] = base64.decodebytes(content["content"].encode("ascii"))
    download = bool(request.args.get("download"))
    kwargs = (
        {"headers": {"Content-Disposition": f"attachment;filename={content['name']}"}}
        if download
        else {}
    )
    mimetype = (
        "text/plain"
        if content.get("mimetype", None) is None
        or content["mimetype"].startswith("text/")
        else content["mimetype"]
    )
    return Response(content["content"], mimetype=mimetype, **kwargs)


@app.route("/api/notebook/private-toc/<path:path>", defaults={"private": True})
@app.route("/api/notebook/toc/<path:path>")
def toc(path, private=False):
    loader = app.private_loader if private else app.contents_loader
    nb = loader.get_nb(path)
    return jsonify(nb.toc())


@app.route("/api/notebook/private-render/<path:path>", defaults={"private": True})
@app.route("/api/notebook/render/<path:path>")
def render_nb(path, private=False):
    loader = app.private_loader if private else app.contents_loader
    nb = loader.get_nb(path)
    return nb.html_content


@app.route("/api/notebook/private-import/<path:path>", defaults={"private": True})
@app.route("/api/notebook/import/<path:path>")
def import_nb(path, private=False):
    base_url = (app.callisto_config.jupyterhub_base_url or "").rstrip("/")
    if not base_url:
        return ""

    if private:
        path = app.private_loader.resolve_path(path)
    path_func = getattr(app.callisto_config, "import_link_func")
    if path_func:
        path = path_func(path, private)

    if getattr(app.callisto_config, "import_link_with_hubshare_preview"):
        return (
            base_url
            + "/user-redirect/?hubshare-preview="
            + base64.b64encode(path.encode("utf-8")).decode("utf-8")
        )

    return base_url + "/user-redirect/lab/tree/" + path


@app.route("/api/encrypt-path")
def encrypt_path():
    path = request.args.get("path")
    return jsonify(
        {"path": path, "encrypted": f"/private/{app.private_loader.encrypt_path(path)}"}
    )


if os.getenv("FLASK_ENV", "") == "development":

    @app.route("/api/private/<path:path>")
    def decrypt(path):
        return app.private_loader.resolve_path(path)


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    output = jsonify({"code": e.code, "name": e.name, "description": e.description})
    response.content_type = "application/json"
    return output, e.code
