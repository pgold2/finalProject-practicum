# from flask import render_template
# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def index():
#     user = {'username': 'Miguel'}
#     return render_template('index.html', title = 'Home', user = user)


from website import create_app

app = create_app()

if __name__ == '__main__': #only if we run this line will the main run on the server
    app.run(debug=True) #any time a change is made to the python code, it automatically re-runs the webserver
