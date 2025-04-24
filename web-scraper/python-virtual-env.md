# Install virtual env
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv

# Create virtual environment
python3 -m venv venv (for Linux)
python -m venv venv (for Windows)

# Activate venv on CMD
venv\Scripts\activate


# Activate venv on Linux
source venv/bin/activate


# install dependencies from requirements.txt file
pip install -r requirements.txt


# Create requirements.txt
pip freeze > requirements.txt

# deactivate environment when needed
deactivate