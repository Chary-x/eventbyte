from flask import Flask, render_template
app = Flask(__name__)

#route to the index
@app.route('/')
def index():
    with open('README.md') as readme:
      with open('requirements.txt') as req:
        return render_template('index.html', README=readme.read(), requirements=req.read())

