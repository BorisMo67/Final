from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///calc.db")


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def club_data(club):
    club_id = db.execute("SELECT id FROM clubs WHERE name = ?", club)[0]["id"]
    coef5 = db.execute("SELECT SUM(points) FROM club_coef WHERE season > 2021 AND club_id = ?", club_id)[
        0]["SUM(points)"]
    if not coef5:
        coef5 = 0
    coef_sep = []
    for i in range(2026, 2021, -1):
        points = db.execute(
            "SELECT points FROM club_coef WHERE season = ? AND club_id = ?", i, club_id)
        if points:
            coef_sep.append(points[0]["points"])
        else:
            coef_sep.append(0)
    coef_coun = db.execute("SELECT SUM(points) FROM country_coef WHERE season > 2021 AND country_id = (SELECT country_id FROM clubs WHERE name = ?)", club)[
        0]["SUM(points)"] * 0.2
    return coef5, round(coef_coun, 3), coef_sep


def check_champ(country):
    a = db.execute(
        """
        SELECT name FROM clubs WHERE id = (
        SELECT club_id FROM champions WHERE country_id = (
        SELECT id FROM countries WHERE name = ?))
        """, country)
    if a:
        return a[0]["name"]


def calc1():
    countries = []
    clubs = []

    list_a = db.execute(
        """
        SELECT c.name, SUM(cc.points)
        FROM country_coef cc JOIN countries c ON c.id = cc.country_id
        WHERE c.name !='liechtenstein' AND cc.season > 2020 AND cc.season < 2026
        GROUP BY c.name ORDER BY SUM(cc.points) DESC
        LIMIT (SELECT COUNT(*) FROM access_list WHERE c1 = 1) OFFSET (SELECT MAX(rank) FROM access_list WHERE c1 = 0)
        """)

    for i in list_a:
        countries.append(i["name"].title())

    for country in countries:
        country = country.lower()
        champ = check_champ(country)

        if champ:
            clubs.append([champ])
        else:
            count = []
            list_b = db.execute("""
                SELECT cl.name, SUM(clc.points)
                FROM club_coef clc JOIN clubs cl ON cl.id = clc.club_id
                WHERE clc.season > 2021 AND cl.country_id = (SELECT id FROM countries WHERE name = ?)
                GROUP BY cl.name ORDER BY SUM(clc.points) DESC
                """, country)

            for i in list_b:
                count.append(i["name"])
            clubs.append(count)
    return countries, clubs


def calc2():
    countries = []
    clubs = []

    list_a = db.execute("""
        SELECT c.name, SUM(cc.points)
        FROM country_coef cc JOIN countries c ON c.id = cc.country_id
        WHERE c.name !='liechtenstein' AND cc.season > 2020 AND cc.season < 2026
        GROUP BY c.name ORDER BY SUM(cc.points) DESC
        LIMIT (SELECT COUNT(*) FROM access_list WHERE c2 = 1) + 1 OFFSET (SELECT MIN(rank) FROM access_list WHERE c2 = 1) - 1
        """)

    for i in list_a:
        countries.append(i["name"].title())

    for country in countries:
        country = country.lower()
        champ = check_champ(country)

        if champ:
            clubs.append([champ])
        else:
            count = []
            list_b = db.execute("""
                SELECT cl.name, SUM(clc.points)
                FROM club_coef clc JOIN clubs cl ON cl.id = clc.club_id
                WHERE clc.season > 2021 AND cl.country_id = (SELECT id FROM countries WHERE name = ?)
                GROUP BY cl.name ORDER BY SUM(clc.points) DESC
                """, country)

            for i in list_b:
                count.append(i["name"])
            clubs.append(count)

    return countries, clubs


def calc4():
    countries = []
    clubs = []

    list_a = db.execute("""
        SELECT c.name, SUM(cc.points)
        FROM country_coef cc JOIN countries c ON c.id = cc.country_id
        WHERE c.name !='liechtenstein' AND cc.season > 2020 AND cc.season < 2026
        GROUP BY c.name ORDER BY SUM(cc.points) DESC
        LIMIT (SELECT COUNT(*) FROM access_list WHERE cpo = 1) OFFSET (SELECT MIN(rank) FROM access_list WHERE cpo = 1) - 1
        """)

    for i in list_a:
        countries.append(i["name"].title())

    for country in countries:
        country = country.lower()
        champ = check_champ(country)

        if champ:
            clubs.append([champ])
        else:
            count = []
            list_b = db.execute("""
                SELECT cl.name, SUM(clc.points)
                FROM club_coef clc JOIN clubs cl ON cl.id = clc.club_id
                WHERE clc.season > 2021 AND cl.country_id = (SELECT id FROM countries WHERE name = ?)
                GROUP BY cl.name ORDER BY SUM(clc.points) DESC
                """, country)

            for i in list_b:
                count.append(i["name"])
            clubs.append(count)

    return countries, clubs
