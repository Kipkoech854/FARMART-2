
# imports('imports needed')
from __init__ import create_app


app = create_app("development")

# register routes and other things here

if __name__ == '__main__':
    app.run(debug = True, host = "0.0.0.0", port = 5555)

