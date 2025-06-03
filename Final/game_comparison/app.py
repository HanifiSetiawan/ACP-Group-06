from flask import Flask, render_template
import xml.etree.ElementTree as ET

def load_games_from_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    games = []
    for item in root.findall('item'):
        game = {child.tag: child.text for child in item}
        games.append(game)
    return games

app = Flask(__name__)

@app.route("/")
def index():
    steam_games = load_games_from_xml('steam_output_playwright(Final_Output).xml')
    xbox_games = load_games_from_xml('xbox_output.xml')
    return render_template("index.html", steam_games=steam_games, xbox_games=xbox_games)

if __name__ == "__main__":
    app.run(debug=True)