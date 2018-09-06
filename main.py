from flask import Flask, render_template, abort, flash, request, jsonify, send_file, redirect, session
import os
import dbcl as db
from util import fetch_bee, parse_bans, parse_rounds, parse_round, send_message, get_patreon_income
import datetime
import config as cfg
import math
import forms
import markdown
import readabledelta
import hashlib
from tok import WEBSITE_TOKEN

app = Flask(__name__)
app.config['SECRET_KEY'] = WEBSITE_TOKEN

@app.route('/signup', methods=['GET', 'POST'])
def page_signup():
    form = forms.SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        passwd = hashlib.sha256(request.form["password"].encode()).hexdigest()
        db.add_user(request.form["username"],passwd,request.form["email"])
        user = db.get_user_from_username(request.form["username"])
        session["username"] = user["username"]
        session["id"] = user["id"]
        session["email"] = user["email"]
        session["admin"] = user["admin"]

        session.permanent = True
        return redirect("/")

    return render_template('signup.html', form=form, session=dict(session))


@app.route('/login', methods=['GET', 'POST'])
def page_login():
    form = forms.LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.get_user_from_username(request.form["username"])
        session["username"] = user["username"]
        session["id"] = user["id"]
        session["email"] = user["email"]
        session["admin"] = user["admin"]
        session.permanent = True
        return redirect("/")

    return render_template('login.html', form=form, session=dict(session))


@app.route('/settings', methods=['GET', 'POST'])
def page_settings():
    form = forms.SettingsForm(request.form)
    if "username" in session:
        user = db.get_user_from_username(session["username"])
        if request.method == 'POST' and form.validate():

            if request.form["avatar"] != "":
                db.update_user(user["id"], "avatar", request.form["avatar"])
            if request.form["ckey"] != "":
                db.update_user(user["id"], "ckey", request.form["ckey"])
            else:
                db.update_user(user["id"], "ckey", None)

            return redirect("/")

        if user["avatar"] != None:
            form.avatar.default=user["avatar"]
        if user["ckey"] != None:
            form.ckey.default=user["ckey"]

        form.process()
        return render_template('settings.html', form=form, session=dict(session))
    else:
        return redirect("/login")

@app.route('/logout', methods=['GET', 'POST'])
def page_logout():
    session.clear()
    return redirect("/")


@app.route("/")
def page_home():
    try:
        currentsts = fetch_bee()

        stats = {
            "duration": str(datetime.timedelta(seconds=int(currentsts["round_duration"]))),
            "players":currentsts["players"],
            "map_name": currentsts["map_name"],
        }
    except:
        stats = {
            "duration": "Error",
            "players":"Error",
            "map_name": "Error",
        }
    income = get_patreon_income()
    budget_stats = {
        "income": "%0.2f" % (income/100,),
        "goal": "%0.2f" % (cfg.BUDGET_GOAL/100,),
        "percent": int(income/cfg.BUDGET_GOAL*100)
    }
    return render_template("home.html", stats=stats, budget_stats=budget_stats)

@app.route("/stats")
def page_stats():
    pastdailysts = db.get_daily_stats()
    pastweeklysts = db.get_weekly_stats()
    try:
        currentsts = fetch_bee()
        clients = [currentsts[key] for key in currentsts.keys() if "client" in key]
        client_groups = [clients[i:i+3] for i in range(0, len(clients), 3)]
        stats = {
            "admins": currentsts["admins"],
            "duration": str(datetime.timedelta(seconds=int(currentsts["round_duration"]))),
            "round": currentsts["round_id"],
            "map": currentsts["map_name"],
            "players":currentsts["players"],
            "mode": currentsts["mode"],
            "dailydata": [stat["players"] for stat in pastdailysts],
            "weeklydata": [stat["players"] for stat in pastweeklysts],
            "dailylabels": [stat["ts"].strftime('%H:%M') for stat in pastdailysts],
            "weeklylabels": [stat["ts"].strftime('%A %H:%M') for stat in pastweeklysts],
            "clients": client_groups
        }



    except Exception as e:

        stats = {
            "admins": "Error",
            "duration": "Error",
            "round": "Error",
            "map": "Error",
            "players":"Error",
            "mode": "Error",
            "dailydata": [stat["players"] for stat in pastdailysts],
            "weeklydata": [stat["players"] for stat in pastweeklysts],
            "dailylabels": [stat["ts"].strftime('%H:%M') for stat in pastdailysts],
            "weeklylabels": [stat["ts"].strftime('%A %H:%M') for stat in pastweeklysts]
        }
    return render_template("stats.html", stats=stats )

@app.route("/rules")
def page_rules():
    return render_template("rules.html")

@app.route("/ses")
def page_session():
    return str(dict(session))

@app.route("/bans")
def page_bans_re():
    return redirect("/bans/1")

@app.route("/bans/<int:page>")
def page_bans(page):
    parse = parse_bans((page-1)*cfg.ITEMS_PER_PAGE, page*cfg.ITEMS_PER_PAGE)
    bans = parse[0]
    length = parse[1]
    buttons = [page > 1, page < length / cfg.ITEMS_PER_PAGE]
    return render_template("bans.html", bans=bans, buttons=buttons, page=page, pages=math.ceil(length / cfg.ITEMS_PER_PAGE))

@app.route("/rounds")
def page_rounds_re():
    return redirect("/rounds/1")

@app.route("/rounds/<int:page>")
def page_rounds(page):
    parse = parse_rounds((page-1)*cfg.ITEMS_PER_PAGE, page*cfg.ITEMS_PER_PAGE)
    rounds = parse[0]
    length = parse[1]
    buttons = [page > 1, page < length / cfg.ITEMS_PER_PAGE]
    return render_template("rounds.html", rounds=rounds, buttons=buttons, page=page, pages=math.ceil(length / cfg.ITEMS_PER_PAGE))

@app.route("/round/<int:round>")
def page_round(round):
    parse = parse_round(round)
    return render_template("round.html", round=parse)

@app.route("/forum")
def page_forum():
    return render_template("topics.html", topics=db.get_topics(),session=session, post_count=db.get_topic_post_count)

@app.route("/forum/<int:topic>")
def page_forum_topic(topic):
    if topic == 0:
        return render_template("posts.html",str=str,dt=datetime,rd=readabledelta.readabledelta, posts=db.posts.find({"origin": None}).sort([["ts", -1]]),session=session, topic=db.get_topic(topic), len=len, reply_count=db.get_post_reply_count)

    else:
        return render_template("posts.html",str=str,dt=datetime,rd=readabledelta.readabledelta, posts=db.get_posts_for_topic(topic),session=session, topic=db.get_topic(topic), len=len, reply_count=db.get_post_reply_count)

@app.route("/forum/<int:topic>/<int:post>", methods=['GET', 'POST'])
def page_forum_topic_post(topic,post):
    form = forms.PostForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.get_user_from_username(session["username"])
        db.add_post(request.form["title"], user["username"], user["id"], request.form["content"], post, topic)
        return redirect("/forum/"+str(topic)+"/"+str(post))
    else:
        p = db.get_full_post(post)
        if request.remote_addr not in p["post"]["views"]:
            db.push_post(post,"views", request.remote_addr)
    def md(text):
        return markdown.markdown(text, output_format="html", extensions=["extra", "nl2br"])
    return render_template("post.html",str=str,dt=datetime,rd=readabledelta.readabledelta,  topic=db.get_topic(topic),session=session, post=p, len=len, get_user=db.get_user, md=md, form=form)

@app.route("/forum/<int:topic>/new", methods=['GET', 'POST'])
def page_forum_topic_new(topic):
    form = forms.PostForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.get_user_from_username(session["username"])
        post = db.add_post(request.form["title"], user["username"], user["id"], request.form["content"], None, topic)
        if topic == 3:
            content = "**"+user["username"]+"** created a **Ban Appeal** called **"+request.form["title"]+"**\n\nhttp://beestation13.com/forum/"+str(topic)+"/"+str(post)
            send_message(cfg.FORUMSLOG, content)
        if topic == 4:
            content = "**"+user["username"]+"** created a **Staff Application** called **"+request.form["title"]+"**\n\nhttp://beestation13.com/forum/"+str(topic)+"/"+str(post)
            send_message(cfg.FORUMSLOG, content)
        if topic == 5:
            content = "**"+user["username"]+"** created a **Player Report** called **"+request.form["title"]+"**\n\nhttp://beestation13.com/forum/"+str(topic)+"/"+str(post)
            send_message(cfg.FORUMSLOG, content)

        return redirect("/forum/"+str(topic)+"/"+str(post))

    return render_template("newpost.html", topic=db.get_topic(topic),session=session, form=form)


@app.route("/forum/<int:topic>/<int:thread>/<int:post>/edit", methods=['GET', 'POST'])
def page_forum_post_edit(topic,thread,post):
    postdt = db.get_post(post)
    form = forms.EditPostForm(request.form)

    if request.method == 'POST' and form.validate():
        user = db.get_user_from_username(session["username"])
        if user["id"] == postdt["authorid"] or user["admin"]:
            db.update_post(postdt["id"], "title", request.form["title"])
            db.update_post(postdt["id"], "content", request.form["content"])
        return redirect("/forum/"+str(topic)+"/"+str(thread)+"#"+str(postdt["id"]))
    else:
        form.title.default=postdt["title"]
        form.content.default=postdt["content"]
        form.process()
        return render_template("editpost.html", topic=db.get_topic(topic),session=session, form=form, postdt=postdt)


@app.route("/forum/<int:topic>/<int:thread>/<int:post>/delete", methods=['GET'])
def page_forum_post_delete(topic,thread,post):
    postdt = db.get_post(post)
    user = db.get_user_from_username(session["username"])
    if user["id"] == postdt["authorid"] or user["admin"]:
        db.delete_post(postdt["id"])
    if postdt["origin"] == None:
        return redirect("/forum/"+str(topic))
    else:
        return redirect("/forum/"+str(topic)+"/"+str(thread)+"#"+str(postdt["id"]))


@app.route("/forum/<int:topic>/<int:thread>/<int:post>/pin", methods=['GET'])
def page_forum_post_pin(topic,thread,post):
    postdt = db.get_post(post)
    user = db.get_user_from_username(session["username"])
    if user["admin"]:
        if postdt["pinned"]:
            db.update_post(postdt["id"], "pinned", False)
        else:
            db.update_post(postdt["id"], "pinned", True)

    return redirect("/forum/"+str(topic)+"/"+str(thread))


@app.route("/heart/<int:topic>/<int:thread>/<int:post>")
def page_heart(topic,thread,post):
    postdt = db.get_post(post)
    user = db.get_user(postdt["authorid"])
    if session["id"] in postdt["upvotes"]:
        db.pull_post(postdt["id"], "upvotes", session["id"])
        db.inc_user(postdt["authorid"], "score", -1)
    elif session["id"] not in postdt["upvotes"]:
        db.push_post(postdt["id"], "upvotes", session["id"])
        db.inc_user(postdt["authorid"], "score", 1)

    return redirect("/forum/"+str(topic)+"/"+str(thread)+"#"+str(postdt["id"]))


@app.route("/static/<string:d1>/<string:d2>")
def page_static(d1,d2):
    return send_file(os.path.join(".", "static", d1, d2))

@app.route("/favicon.ico")
def page_favicon():
    return send_file(os.path.join(".", "static", "img", "logo.png"))

@app.route("/api/stats")
def page_api_stats():
    try:
        return jsonify(fetch_bee())
    except:
        return jsonify({"error": "unknown"})

@app.route("/api/bans")
def page_api_bans():
    try:
        return jsonify(parse_bans(0,1000000)[0])
    except:
        return jsonify({"error": "unknown"})


@app.route("/api/round/<int:roundid>")
def page_api_round(roundid):
    try:
        return jsonify(parse_round(roundid))
    except IndexError:
        return jsonify({"error": "round not found"})
    except:
        return jsonify({"error": "unknown"})

@app.route("/api/lastround")
def page_api_lastround():
    try:
        return jsonify(parse_rounds(0,1))
    except:
        return jsonify({"error": "unknown"})


@app.route("/test")
def page_test():
    return render_template("test.html")
