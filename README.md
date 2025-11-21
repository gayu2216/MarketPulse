# MarketPulse

Install dependencies:
# create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# upgrade pip and install requirements
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt


python run.py

python -m debugpy --listen 5678 --wait-for-client run.py

Sample test case run:
python -m pytest tests/test_delete_account_controller.py -v