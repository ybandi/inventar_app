
# A very simple Flask Hello World app for you to get started with...

#from flask import Flask

#app = Flask(__name__)

#@app.route('/')
#def hello_world():
#    return 'Hello from Flask!'


from app import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():  # Create an application context
        db.create_all()    # NOW it's safe to create the tables
    app.run(debug=True)  # Set debug=False for production!
