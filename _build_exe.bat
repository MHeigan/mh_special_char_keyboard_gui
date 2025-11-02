pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed ^
  --name mh_special_char_keyboard ^
  --version-file file_version_info.txt ^
  mh_special_char_keyboard_gui.py
