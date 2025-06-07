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
    steam_games = load_games_from_xml('steam_output_playwright.xml')
    xbox_games = load_games_from_xml('xbox_output.xml')

    # Merge by name (case-insensitive)
    merged = {}
    for game in steam_games:
        name = game['name'].strip().lower()
        merged[name] = {
            "name": game['name'],
            "steam_price": game['final_price'],
            "xbox_price": None
        }
    for game in xbox_games:
        name = game['name'].strip().lower()
        if name in merged:
            merged[name]["xbox_price"] = game['final_price']
        else:
            merged[name] = {
                "name": game['name'],
                "steam_price": None,
                "xbox_price": game['final_price']
            }
    merged_games = list(merged.values())

    return render_template("index.html", merged_games=merged_games)
if __name__ == "__main__":
    app.run(debug=True)