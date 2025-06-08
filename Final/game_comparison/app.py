from flask import Flask, render_template, request
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

def usd_to_ntd(price_str, rate=30):
    if not price_str or not price_str.startswith('$'):
        return None
    try:
        usd = float(price_str.replace('$', '').replace(',', '').strip())
        ntd = int(round(usd * rate))
        return f"NT$ {ntd}.00"
    except Exception:
        return None

@app.route("/")
def index():
    steam_games = load_games_from_xml('steam_output_playwright_img.xml')
    xbox_games = load_games_from_xml('xbox_output_img.xml')
    ps_games = load_games_from_xml('ps_output_img.xml')
    epic_games = load_games_from_xml('epic_output.xml')

    # Merge by name (case-insensitive)
    merged = {}
    for game in steam_games:
        name = game['name'].strip().lower()
        merged[name] = {
            "image": game.get('image_url', None),
            "name": game['name'],
            "steam_price": game['final_price'],
            "xbox_price": None,
            "ps_price": None,
            "epic_price": None
        }
    for game in xbox_games:
        name = game['name'].strip().lower()
        ntd_price = usd_to_ntd(game['final_price'])
        if name in merged:
            merged[name]["xbox_price"] = ntd_price
        else:
            merged[name] = {
                "image": game.get('image_url', None),
                "name": game['name'],
                "steam_price": None,
                "xbox_price": ntd_price,
                "ps_price": None,
                "epic_price": None
            }
    for game in ps_games:
        name = game['name'].strip().lower()
        ntd_price = usd_to_ntd(game['final_price'])
        if name in merged:
            merged[name]["ps_price"] = ntd_price
        else:
            merged[name] = {
                "image": game.get('image_url', None),
                "name": game['name'],
                "steam_price": None,
                "xbox_price": None,
                "ps_price": ntd_price,
                "epic_price": None
            }
    for game in epic_games:
        name = game['name'].strip().lower()
        ntd_price = usd_to_ntd(game['final_price'])
        if name in merged:
            merged[name]["epic_price"] = ntd_price
        else:
            merged[name] = {
                "image": game.get('image_url', None),
                "name": game['name'],
                "steam_price": None,
                "xbox_price": None,
                "ps_price": None,
                "epic_price": ntd_price
            }
    merged_games = list(merged.values())
    merged_games.sort(key=lambda x: x['name'])  # Optional: sort by name

    query = request.args.get("q", "").strip().lower()
    if query:
        merged_games = [g for g in merged_games if query in g['name'].lower()]

    # Pagination logic  # Make sure this import is at the top of your file
    page = int(request.args.get("page", 1))
    per_page = 100
    total = len(merged_games)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_games = merged_games[start:end]

    return render_template(
        "index.html",
        merged_games=paginated_games,
        page=page,
        pages=pages,
        query=query
    )
if __name__ == "__main__":
    app.run(debug=True)