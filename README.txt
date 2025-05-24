! Make sure that pip IS ADDED to PATH 
# TO INSTALL PACKAGES (pygame, chess, pipwin, cairosvg, cairocffi), EXEUCUTE IN COMMAND PROMPT(cmd) FROM LOCAL DIRECTORY ("PyChess"):

(ONLINE METHOD - RECOMMENDED)
pip install -r requirements.txt && pipwin install cairocffi

(OFFLINE METHOD)
pip install -r wheelhouse/requirements.txt --no-index --find-links wheelhouse && pip install pipwin_wheelhouse/cairocffi-1.3.0-cp310-cp310-win_amd64.whl

# RUN 'PyChess.py' or  'PyChess.exe' TO START GAME

# MERITS OF PyChess:
- Game menu implementation
- All completed games are archived
- Options to edit and delete archives
- UI is more polished than previous versions
- Piece selection
- Check and checkmate detection
- Sound effects

# DEMERITS OF PyChess:
- Slight input latency due to SVG to PNG conversion