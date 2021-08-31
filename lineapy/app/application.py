from __init__ import create_app

app = create_app()
if __name__ == "__main__":
    app.run(port=4000)
