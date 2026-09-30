from dotenv import load_dotenv

load_dotenv()

from chatbot_template.app import create_app  # noqa: E402

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5050, debug=True)
