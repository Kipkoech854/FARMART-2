from App import create_app


app = create_app(config_name='production')

if __name__ == "__main__":
    
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
