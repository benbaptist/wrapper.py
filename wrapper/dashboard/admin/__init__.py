from flask import Flask, redirect, url_for, render_template, \
    request, make_response, Response, Markup, Blueprint, current_app, g

from wrapper.exceptions import *

blueprint_admin = Blueprint("admin", __name__,
        template_folder="templates")

@blueprint_admin.before_request
def before_request():
    g.wrapper = current_app.wrapper
    g.verify_token = current_app.wrapper.dashboard.auth.verify_token

    try:
        g.username = g.verify_token()
    except AuthError:
        return redirect("/login")

@blueprint_admin.route("/", methods=["GET"])
def landing():
    return render_template("landing.html")

@blueprint_admin.route("/chat", methods=["GET"])
def chat():
    return render_template("chat.html")

@blueprint_admin.route("/players", methods=["GET"])
def players():
    return render_template("players.html")

@blueprint_admin.route("/players/<path:mcuuid>", methods=["GET"])
def players_player(mcuuid):
    player = g.wrapper.server.get_player_(mcuuid=mcuuid)

    print(player)
    return render_template("players.player.html", player=player)

@blueprint_admin.route("/config", methods=["GET"])
def config():
    return render_template("config.html")

@blueprint_admin.route("/versions", methods=["GET"])
def versions():
    if "download" in request.args:
        version = request.args["download"]
        g.wrapper.mojang.servers.get_jar(version)

    return render_template("versions.html")

@blueprint_admin.route("/backups", methods=["GET"])
def backups_list():
    if "delete" in request.args:
        backup_id = request.args["delete"]

        g.wrapper.backups.delete(backup_id)

    return render_template("backups_list.html")

@blueprint_admin.route("/backups/settings", methods=["GET"])
def backups_settings():
    return render_template("backups_settings.html")

@blueprint_admin.route("/plugins", methods=["GET"])
def plugins():
    if "reload" in request.args:
        g.wrapper.plugins.reload_plugins()
        
    return render_template("plugins.html")
