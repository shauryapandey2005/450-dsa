from app import create_app


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me-to-a-random-string')
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
