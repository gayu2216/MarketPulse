from src.app import app

import os

if __name__ == "__main__":
    if os.environ.get("DEBUGPY") == "1":
        app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
    else:
        app.run(host="127.0.0.1", port=5000, debug=True)