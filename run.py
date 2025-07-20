from App import create_app

app = create_app()

if __name__ == "__main__":
    # Render uses port 10000 by default
    app.run(host='0.0.0.0', port=10000)
