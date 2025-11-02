cd mh_special_char_keyboard
# optional venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# init + first commit
# Windows:
init_repo.bat
# macOS/Linux:
chmod +x init_repo.sh && ./init_repo.sh

# add remote & push
git remote add origin https://github.com/<youruser>/mh_special_char_keyboard.git
git push -u origin main
