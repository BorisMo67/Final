import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from functions import club_data, check_champ, calc1, calc2, calc4, login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///calc.db")


@app.route("/login", methods = ["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("apology.html", message="Must provide username", code=400)
        elif not request.form.get("password"):
            return render_template("apology.html", message="Must provide password", code=400)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("apology.html", message="Invalid username/password", code=400)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if request.method == "POST":
        if not username:
            return render_template("apology.html", message="Must provide username", code=400)
        elif len(username) < 5:
            return render_template("apology.html", message="Username too short", code=400)
        elif not password:
            return render_template("apology.html", message="Must provide password", code=400)
        elif len(password) < 6:
            return render_template("apology.html", message="Please use longer password", code=400)
        elif password != request.form.get("confirmation"):
            return render_template("apology.html", message="Passwords do not match", code=400)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       username, generate_password_hash(password))
        except ValueError:
            return render_template("apology.html", message="Username already exists, try another one.", code=400)

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    ucl, uel, uecl = [], [], []
    active_ucl = db.execute(
        "SELECT name FROM clubs WHERE id IN (SELECT club_id FROM active WHERE comp = 'ucl') ORDER BY name")
    active_uel = db.execute(
        "SELECT name FROM clubs WHERE id IN (SELECT club_id FROM active WHERE comp = 'uel') ORDER BY name")
    active_uecl = db.execute(
        "SELECT name FROM clubs WHERE id IN (SELECT club_id FROM active WHERE comp = 'uecl') ORDER BY name")

    for club in active_ucl:
        ucl.append(club["name"])
    for club in active_uel:
        uel.append(club["name"])
    for club in active_uecl:
        uecl.append(club["name"])

    if request.method == "POST":

        for club in ucl:
            result = request.form.get(club)
            if result == 'w':
                db.execute(
                    "UPDATE club_coef SET points = points + 2 WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", club)
            elif result == 'd':
                db.execute(
                    "UPDATE club_coef SET points = points + 1 WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", club)

        for club in uel:
            result = request.form.get(club)
            current = db.execute(
                "SELECT points FROM club_coef WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", club)[0]["points"]
            if result == 'w':
                db.execute(
                    "UPDATE active SET points = points + 2 WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)
                temp = db.execute(
                    "SELECT points FROM active WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)[0]["points"]
                if temp > current:
                    db.execute(
                        "UPDATE club_coef SET points = ? WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", temp, club)
            elif result == 'd':
                db.execute(
                    "UPDATE active SET points = points + 1 WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)
                temp = db.execute(
                    "SELECT points FROM active WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)[0]["points"]
                if temp > current:
                    db.execute(
                        "UPDATE club_coef SET points = ? WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", temp, club)

        for club in uecl:
            result = request.form.get(club)
            current = db.execute(
                "SELECT points FROM club_coef WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", club)[0]["points"]
            if result == 'w':
                db.execute(
                    "UPDATE active SET points = points + 2 WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)
                temp = db.execute(
                    "SELECT points FROM active WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)[0]["points"]
                if temp > current:
                    db.execute(
                        "UPDATE club_coef SET points = ? WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", temp, club)
            elif result == 'd':
                db.execute(
                    "UPDATE active SET points = points + 1 WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)
                temp = db.execute(
                    "SELECT points FROM active WHERE club_id = (SELECT id FROM clubs WHERE name = ?)", club)[0]["points"]
                if temp > current:
                    db.execute(
                        "UPDATE club_coef SET points = ? WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", temp, club)

        return redirect("/")

    else:
        return render_template("update.html", ucl=ucl, uel=uel, uecl=uecl)


@app.route("/update_standings", methods=["GET", "POST"])
@login_required
def update_standings():
    ucl, uel, uecl = [], [], []
    active_ucl = db.execute(
        "SELECT name FROM clubs WHERE id IN (SELECT club_id FROM active WHERE comp = 'ucl') ORDER BY name")
    active_uel = db.execute(
        "SELECT name FROM clubs WHERE id IN (SELECT club_id FROM active WHERE comp = 'uel') ORDER BY name")
    active_uecl = db.execute(
        "SELECT name FROM clubs WHERE id IN (SELECT club_id FROM active WHERE comp = 'uecl') ORDER BY name")

    for club in active_ucl:
        ucl.append(club["name"])
    for club in active_uel:
        uel.append(club["name"])
    for club in active_uecl:
        uecl.append(club["name"])

    if request.method == "POST":

        for club in ucl:
            # result = request.form.get(club)
            # points = 12 - (result - 1) * 0.25
            # if points < 6:
            #     points = 6
            result = request.form.get(club)
            points = 6 - (result - 1) * 0.25
            if points < 0:
                points = 0
            db.execute(
                "UPDATE club_coef SET points = points + ? WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", points, club)

        for club in uel:
            result = request.form.get(club)
            points = 6 - (result - 1) * 0.25
            if points < 0:
                points = 0
            db.execute(
                "UPDATE club_coef SET points = points + ? WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", points, club)

        for club in uecl:
            result = request.form.get(club)
            if result < 9:
                points = 4 - (result - 1) * 0.25
            elif result < 25:
                points = 2 - (result - 9) * 0.125
            else:
                points = 0
            db.execute(
                "UPDATE club_coef SET points = points + ? WHERE season = 2026 AND club_id = (SELECT id FROM clubs WHERE name = ?)", points, club)

        return redirect("/")

    else:
        return render_template("standings.html", ucl=ucl, uel=uel, uecl=uecl)



@app.route("/update_ko", methods=["GET", "POST"])
@login_required
def update_ko():
    ...


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/first", methods=["GET", "POST"])
def first():

    if request.method == "POST":

        champs = []
        champs_dict = request.form.to_dict()

        # Check UCL-th checkbox
        if request.form.get("UCL-th"):
            champs_dict.pop("UCL-th", None)
            ucl_th = True
        else:
            ucl_th = False

        # Get coefficient and sort clubs
        for key, value in champs_dict.items():
            club_coef, country_coef, last5 = club_data(value)
            coef = max(club_coef, country_coef)
            champs.append({"name": value, "coef": coef, "last5": last5})

        sorted_champs = sorted(
            champs,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )  # used chatGPT to sort a list

        result = [(c["name"], c["coef"]) for c in sorted_champs]

        # Generate seeding table for selected clubs
        if ucl_th == True:
            return render_template("seeding.html", champs=result[2:])
        else:
            return render_template("seeding.html", champs=result)

    else:

        countries, clubs = calc1()

        return render_template("first.html", clubs=clubs, countries=countries)


@app.route("/second", methods=["GET", "POST"])
def second():

    if request.method == "POST":

        champs = []
        first = []
        champs_dict = request.form.to_dict()

        # Check UCL-th checkbox
        if request.form.get("UCL-th"):
            champs_dict.pop("UCL-th", None)
            ucl_th = True
        else:
            ucl_th = False

        # Get coefficient and sort clubs
        for key, value in champs_dict.items():
            club_coef, country_coef, last5 = club_data(value)
            coef = max(club_coef, country_coef)
            if key[0] == '$':
                champs.append({"name": value, "coef": coef, "last5": last5})
            else:
                first.append({"name": value, "coef": coef, "last5": last5})

        sorted_first = sorted(
            first,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )

        champs = sorted(
            champs,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )

        if ucl_th == True:
            champs = champs[1:]

        half = len(sorted_first) // 2
        if ucl_th == True:
            half += 1

        for i in range(half):
            champs.append(sorted_first[i])

        sorted_champs = sorted(
            champs,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )  # used chatGPT to sort a list

        result = [(c["name"], c["coef"]) for c in sorted_champs]

        return render_template("seeding.html", champs=result)

    else:

        countries1, clubs1 = calc1()
        countries2, clubs2 = calc2()

        return render_template("second.html", clubs1=clubs1, countries1=countries1, clubs2=clubs2, countries2=countries2, rnd='2nd')


@app.route("/third", methods=["GET", "POST"])
def third():

    if request.method == "POST":

        champs = []
        first = []
        champs_dict = request.form.to_dict()

        # Check UCL-th checkbox
        if request.form.get("UCL-th"):
            champs_dict.pop("UCL-th", None)
            ucl_th = True
        else:
            ucl_th = False

        # Get coefficient and sort clubs
        for key, value in champs_dict.items():
            club_coef, country_coef, last5 = club_data(value)
            coef = max(club_coef, country_coef)
            if key[0] == '$':
                champs.append({"name": value, "coef": coef, "last5": last5})
            else:
                first.append({"name": value, "coef": coef, "last5": last5})

        sorted_first = sorted(
            first,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )

        champs = sorted(
            champs,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )

        if ucl_th == True:
            champs = champs[1:]

        half = len(sorted_first) // 2
        if ucl_th == True:
            half += 1

        for i in range(half):
            champs.append(sorted_first[i])

        sorted_champs = sorted(
            champs,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )  # used chatGPT to sort a list

        half = len(sorted_champs) // 2
        if ucl_th == True:
            half += 1

        result = [(sorted_champs[i]["name"], sorted_champs[i]["coef"]) for i in range(half)]

        return render_template("seeding.html", champs=result)

    else:

        countries1, clubs1 = calc1()
        countries2, clubs2 = calc2()

        return render_template("second.html", clubs1=clubs1, countries1=countries1, clubs2=clubs2, countries2=countries2, rnd='3rd')


@app.route("/playoff", methods=["GET", "POST"])
def playoff():

    if request.method == "POST":

        champs = []
        first = []
        second = []
        champs_dict = request.form.to_dict()

        # Check UCL-th checkbox
        if request.form.get("UCL-th"):
            champs_dict.pop("UCL-th", None)
            ucl_th = True
        else:
            ucl_th = False

        # Get coefficient and sort clubs
        for key, value in champs_dict.items():
            club_coef, country_coef, last5 = club_data(value)
            coef = max(club_coef, country_coef)
            if key[0] == '&':
                champs.append({"name": value, "coef": coef, "last5": last5})
            elif key[0] == '$':
                second.append({"name": value, "coef": coef, "last5": last5})
            else:
                first.append({"name": value, "coef": coef, "last5": last5})

        sorted_first = sorted(
            first,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )

        half = len(sorted_first) // 2
        if ucl_th == True:
            half += 1

        for i in range(half):
            second.append(sorted_first[i])

        sorted_second = sorted(
            second,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )  # used chatGPT to sort a list

        quarter = len(sorted_second) // 4
        if ucl_th == True:
            quarter += 1

        for i in range(quarter):
            champs.append(sorted_second[i])

        sorted_champs = sorted(
            champs,
            key=lambda c: (c["coef"], *c["last5"]),
            reverse=True
        )  # used chatGPT to sort a list

        result = [(sorted_champs[i]["name"], sorted_champs[i]["coef"]) for i in range(len(sorted_champs))]

        # Generate seeding table for selected clubs
        if ucl_th == True:
            return render_template("seeding.html", champs=result[1:])
        else:
            return render_template("seeding.html", champs=result)

    else:

        countries1, clubs1 = calc1()
        countries2, clubs2 = calc2()
        countries4, clubs4 = calc4()

        return render_template("playoff.html", clubs1=clubs1, countries1=countries1, clubs2=clubs2, countries2=countries2, clubs4=clubs4, countries4=countries4)


@app.route("/clranking")
def clranking():

    rows = db.execute("""
        SELECT
            c.name AS club,
            co.name AS country,
            SUM(CASE WHEN cc.season = 2022 THEN cc.points ELSE 0 END) AS s2022,
            SUM(CASE WHEN cc.season = 2023 THEN cc.points ELSE 0 END) AS s2023,
            SUM(CASE WHEN cc.season = 2024 THEN cc.points ELSE 0 END) AS s2024,
            SUM(CASE WHEN cc.season = 2025 THEN cc.points ELSE 0 END) AS s2025,
            SUM(CASE WHEN cc.season = 2026 THEN cc.points ELSE 0 END) AS s2026,
            SUM(CASE WHEN cc.season BETWEEN 2022 AND 2026 THEN cc.points ELSE 0 END) AS total,
            0.2 * (
                SELECT SUM(points)
                FROM country_coef AS coc
                WHERE coc.country_id = co.id
                AND coc.season BETWEEN 2022 AND 2026
            ) AS country_c
        FROM clubs AS c
        JOIN countries AS co ON co.id = c.country_id
        LEFT JOIN club_coef AS cc ON cc.club_id = c.id
        GROUP BY c.id
        ORDER BY total DESC
        """)  # Originally generated data for each club individually, but page took too long to load, so used chatGPT to make program run faster

    sorted_data = sorted(
            rows,
            key=lambda c: (
                max(c["total"], c["country_c"]),
                c["s2026"], c["s2025"], c["s2024"], c["s2023"], c["s2022"],
                c["country_c"]),
            reverse=True
        )

    return render_template("clranking.html", data=sorted_data)


@app.route("/coranking")
def coranking():
    rows = db.execute("""
        SELECT
            co.name AS name,
            SUM(CASE WHEN cc.season = 2022 THEN cc.points ELSE 0 END) AS s2022,
            SUM(CASE WHEN cc.season = 2023 THEN cc.points ELSE 0 END) AS s2023,
            SUM(CASE WHEN cc.season = 2024 THEN cc.points ELSE 0 END) AS s2024,
            SUM(CASE WHEN cc.season = 2025 THEN cc.points ELSE 0 END) AS s2025,
            SUM(CASE WHEN cc.season = 2026 THEN cc.points ELSE 0 END) AS s2026,
            SUM(CASE WHEN cc.season BETWEEN 2022 AND 2026 THEN cc.points ELSE 0 END) AS total
        FROM countries AS co JOIN country_coef AS cc
        ON co.id = cc.country_id
        GROUP BY co.id
        ORDER BY total DESC
        """)

    return render_template("coranking.html", data=rows)


'''
-Pokusati skontati update_standings of ChatGPTi testirati nekako
-Dodati update_ko
-Razdvojiti update i update_standings za 3 natjecanja (da se mogu unositi posebno)
-Skontati update za drzavni koef
Rijesiti velika slova u imenima klubova
Dodati ostale klubove iz lige
Opcionalno: ponuditi samo klubove koji jos mogu postati prvaci
'''
