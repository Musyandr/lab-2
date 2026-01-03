from flask import Flask, render_template, request, redirect, url_for
import re
from datetime import datetime
app = Flask(__name__)

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        age = request.form.get("age")
        comment = request.form.get("comment")
        errors = []
        if not name:
            errors.append("Поле Ім'я не може бути порожнім.")
        if not email:
            errors.append("Поле Email не може бути порожнім.")
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if email and not re.match(email_regex, email):
            errors.append("Неправильний формат Email.")
        if not age:
            errors.append("Поле Вік не може бути порожнім.")
        if age and not age.isdigit():
            errors.append("Поле Вік повинно містити тільки цифри.")
        if not comment:
            errors.append("Поле Коментар не може бути порожнім.")
        if errors:
            return render_template("form.html", errors=errors, name=name, email=email, age=age, comment=comment)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"submission_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Ім'я: {name}\n")
            file.write(f"Email: {email}\n")
            file.write(f"Вік: {age}\n")
            file.write(f"Коментар: {comment}\n")
        return redirect(url_for("result", name=name, email=email, age=age, comment=comment, filename=filename))
    return render_template("form.html")

@app.route("/result")
def result():
    name = request.args.get("name", "")
    email = request.args.get("email", "")
    age = request.args.get("age", "")
    comment = request.args.get("comment", "")
    filename = request.args.get("filename", "")
    return render_template("result.html", name=name, email=email, age=age, comment=comment, filename=filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
