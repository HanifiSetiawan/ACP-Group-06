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
    steam_games = load_games_from_xml('steam_output_img_link.xml')
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
            "steam_link": game.get('link', None),
            "xbox_price": None,
            "xbox_link": None,
            "ps_price": None,
            "ps_link": None,
            "epic_price": None,
            "epic_link": None
        }
    for game in xbox_games:
        name = game['name'].strip().lower()
        ntd_price = usd_to_ntd(game['final_price'])
        if name in merged:
            merged[name]["xbox_price"] = ntd_price
            merged[name]["xbox_link"] = game.get('url', None)
        else:
            merged[name] = {
                "image": game.get('image_url', None),
                "name": game['name'],
                "steam_price": None,
                "steam_link": None,
                "xbox_price": ntd_price,
                "xbox_link": game.get('url', None),
                "ps_price": None,
                "ps_link": None,
                "epic_price": None,
                "epic_link": None
            }
    for game in ps_games:
        name = game['name'].strip().lower()
        ntd_price = usd_to_ntd(game['final_price'])
        if name in merged:
            merged[name]["ps_price"] = ntd_price
            merged[name]["ps_link"] = game.get('link', None)
        else:
            merged[name] = {
                "image": game.get('image_url', None),
                "name": game['name'],
                "steam_price": None,
                "steam_link": None,
                "xbox_price": None,
                "xbox_link": None,
                "ps_price": ntd_price,
                "ps_link": game.get('link', None),
                "epic_price": None,
                "epic_link": None
            }
    for game in epic_games:
        name = game['name'].strip().lower()
        ntd_price = usd_to_ntd(game['final_price'])
        if name in merged:
            merged[name]["epic_price"] = ntd_price
            merged[name]["epic_link"] = game.get('link', None)
        else:
            merged[name] = {
                "image": game.get('image_url', None),
                "name": game['name'],
                "steam_price": None,
                "steam_link": None,
                "xbox_price": None,
                "xbox_link": None,
                "ps_price": None,
                "ps_link": None,
                "epic_price": ntd_price,
                "epic_link": game.get('link', None)
            }
    merged_games = list(merged.values())
    # Sort by number of non-None prices (descending)
    def price_count(game):
        return sum([
            game.get("steam_price") is not None,
            game.get("xbox_price") is not None,
            game.get("ps_price") is not None,
            game.get("epic_price") is not None
        ])
    merged_games.sort(key=price_count, reverse=True)

    query = request.args.get("q", "").strip().lower()
    if query:
        merged_games = [g for g in merged_games if query in g['name'].lower()]

    # Pagination logic
    page = int(request.args.get("page", 1))
    per_page = 10
    total = len(merged_games)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_games = merged_games[start:end]

    # Sliding window pagination variables
    max_pages_to_show = 8
    window_start = ((page - 1) // max_pages_to_show) * max_pages_to_show + 1
    window_end = window_start + max_pages_to_show - 1

    return render_template(
        "index.html",
        merged_games=paginated_games,
        page=page,
        pages=pages,
        query=query,
        max_pages_to_show=max_pages_to_show,
        window_start=window_start,
        window_end=window_end
    )
if __name__ == "__main__":
    app.run(debug=True)