from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/hello2")
def hello2():
    name = request.args.get("name")
    return render_template("hello.html.j2", name=name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
