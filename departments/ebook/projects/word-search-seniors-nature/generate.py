"""
Large Print Word Search for Seniors - Calming Nature Edition
8.5x11, 50 puzzles, 15x15 grid, large print, answer key
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import random
import string

PDF_PATH = Path(__file__).parent / "Word_Search_Seniors_Nature_Interior.pdf"
W, H = letter
M = 0.75 * inch

NAVY = HexColor("#2C3E50")
GREEN = HexColor("#27AE60")
LIGHT = HexColor("#ECF0F1")
TEXT = HexColor("#2C3E50")
GRAY = HexColor("#95A5A6")
GOLD = HexColor("#D4AC0D")

GRID_N = 15

# 50 nature-themed puzzles, each with a list of words
PUZZLES = [
    ("MORNING GARDEN", ["ROSE","TULIP","DAISY","LILY","PEONY","DAFFODIL","IRIS","PANSY","ORCHID","JASMINE","LAVENDER","SUNFLOWER"]),
    ("FOREST WALK", ["OAK","PINE","MAPLE","BIRCH","CEDAR","FERN","MOSS","ACORN","BARK","TRAIL","CANOPY","STREAM"]),
    ("BEACH DAY", ["SAND","SHELL","WAVE","TIDE","CRAB","SEAGULL","SUNSET","ROCK","CORAL","DRIFTWOOD","BEACH","SALTY"]),
    ("MOUNTAIN AIR", ["PEAK","RIDGE","CLIFF","VALLEY","SUMMIT","SLOPE","PINE","SNOW","BOULDER","MEADOW","GLACIER","CABIN"]),
    ("GARDEN BIRDS", ["ROBIN","SPARROW","FINCH","WREN","BLUEJAY","CARDINAL","DOVE","CROW","HAWK","OWL","SWALLOW","STARLING"]),
    ("KITCHEN HERBS", ["BASIL","THYME","SAGE","MINT","CHIVE","DILL","PARSLEY","OREGANO","ROSEMARY","CILANTRO","LEMON","GINGER"]),
    ("BUTTERFLY MEADOW", ["MONARCH","SWALLOW","COPPER","NECTAR","COCOON","WING","PETAL","CLOVER","DAISY","BEE","POLLEN","SUMMER"]),
    ("WOODLAND ANIMALS", ["DEER","FOX","RABBIT","SQUIRREL","BADGER","OTTER","BEAVER","RACCOON","SKUNK","MOUSE","BEAR","ELK"]),
    ("AUTUMN LEAVES", ["GOLD","AMBER","SCARLET","RUST","CRIMSON","ORANGE","YELLOW","BROWN","CRISP","FALL","HARVEST","ACORN"]),
    ("WINTER MORNING", ["SNOW","FROST","ICE","CHILL","WINTER","FLAKE","BREATH","COZY","BLANKET","HEARTH","CABIN","WARMTH"]),
    ("SPRING BLOOMS", ["TULIP","CROCUS","DAFFODIL","HYACINTH","PRIMROSE","BLOSSOM","BUD","RAIN","RENEWAL","FRESH","GARDEN","BIRDSONG"]),
    ("SUMMER PICNIC", ["BASKET","BLANKET","BREEZE","SHADE","LEMONADE","SANDWICH","MEADOW","PARK","SUNLIGHT","LAUGH","FAMILY","PICNIC"]),
    ("OCEAN BREEZE", ["SAILBOAT","HORIZON","SEAGULL","BREEZE","SALT","TIDE","CURRENT","DEEP","WAVE","SHORE","HARBOR","ANCHOR"]),
    ("DESERT CALM", ["CACTUS","DUNE","SAND","OASIS","SUNSET","STAR","SAGEBRUSH","COYOTE","CANYON","MESA","SILENCE","HORIZON"]),
    ("RIVER WALK", ["CURRENT","STONE","BRIDGE","WILLOW","DRAGONFLY","TROUT","RIPPLE","REED","BANK","FISHING","CALM","FLOW"]),
    ("VEGETABLE GARDEN", ["TOMATO","CARROT","ONION","PEPPER","SQUASH","BEAN","LETTUCE","RADISH","CUCUMBER","GARLIC","POTATO","SPINACH"]),
    ("FRUIT ORCHARD", ["APPLE","PEACH","PEAR","PLUM","CHERRY","APRICOT","FIG","ORANGE","LEMON","GRAPE","BERRY","MANGO"]),
    ("BACKYARD POND", ["LILY","KOI","FROG","DRAGONFLY","RIPPLE","REED","TURTLE","HERON","TADPOLE","CATTAIL","STONE","ALGAE"]),
    ("STARRY NIGHT", ["MOON","STAR","COMET","ORION","DIPPER","NEBULA","GALAXY","TWINKLE","DARK","MIDNIGHT","COSMOS","SILENCE"]),
    ("MORNING DEW", ["DEW","GRASS","MIST","SUNRISE","HORIZON","BREEZE","CALM","QUIET","GENTLE","BIRD","FRESH","DAWN"]),
    ("COZY FIREPLACE", ["LOG","FLAME","HEARTH","EMBER","CRACKLE","WARMTH","CHAIR","BLANKET","TEA","BOOK","CANDLE","HOME"]),
    ("RAIN SHOWER", ["DROP","CLOUD","PUDDLE","UMBRELLA","WINDOW","SOAK","REFRESH","RAINBOW","WET","COZY","STORM","PATTER"]),
    ("HONEYBEE BUZZ", ["HONEY","HIVE","COMB","NECTAR","POLLEN","QUEEN","WORKER","DRONE","FLOWER","WING","BUZZ","WAX"]),
    ("FARM MORNING", ["BARN","ROOSTER","HEN","HORSE","COW","SHEEP","FENCE","HAYLOFT","PASTURE","TRACTOR","FIELD","SUNRISE"]),
    ("TEA GARDEN", ["CHAMOMILE","ROSEHIP","MINT","HONEY","TEACUP","SAUCER","STEAM","KETTLE","LEAF","HERB","BREW","CALM"]),
    ("LIGHTHOUSE COAST", ["BEACON","TOWER","ROCKY","FOG","HORN","KEEPER","SAFE","NIGHT","SHIP","GUIDE","STORM","HARBOR"]),
    ("FRESH BREAD", ["DOUGH","FLOUR","YEAST","KNEAD","CRUST","SLICE","OVEN","WARM","BUTTER","JAM","LOAF","BAKERY"]),
    ("FALL HARVEST", ["PUMPKIN","APPLE","CORN","HAY","BARN","CROP","BUSHEL","FARMER","SCARECROW","GOURD","BASKET","CIDER"]),
    ("EVENING STROLL", ["SUNSET","PATH","BENCH","LAMPPOST","WALK","BREEZE","HOLD","HAND","CALM","TALK","HOMEWARD","MOONRISE"]),
    ("HUMMINGBIRD VISIT", ["HUMMING","WING","NECTAR","FEEDER","RUBY","HOVER","PETAL","TINY","SWIFT","BLOOM","JOY","SUMMER"]),
    ("ANTIQUE PARLOR", ["LACE","CLOCK","PORTRAIT","TEAPOT","DOILY","CHAIR","PIANO","LAMP","VELVET","BRASS","OAK","HEIRLOOM"]),
    ("MARKET STALL", ["BREAD","HONEY","JAM","CHEESE","BERRY","FLOWER","BASKET","COIN","FRESH","FARMER","APRON","SMILE"]),
    ("CABIN RETREAT", ["FIRE","LOG","KETTLE","ROCKER","QUILT","PINE","STARS","COCOA","WARM","REST","SILENCE","CALM"]),
    ("SUNRISE ON LAKE", ["MIRROR","STILL","RIPPLE","DOCK","CANOE","LOON","SUNRISE","REED","SHORE","DEW","REFLECT","PEACE"]),
    ("ENGLISH COTTAGE", ["IVY","ROSE","HEDGE","COBBLE","CHIMNEY","THATCH","DOOR","WINDOW","GARDEN","TEA","WARMTH","HOME"]),
    ("WILDFLOWER FIELD", ["DAISY","POPPY","CLOVER","BUTTERCUP","BLUEBELL","THISTLE","FERN","BEE","BREEZE","PETAL","STEM","BLOOM"]),
    ("KITCHEN GARDEN", ["BASIL","TOMATO","BEAN","PEA","CHIVE","DILL","KALE","SAGE","MINT","CARROT","PEPPER","HERB"]),
    ("PINEWOOD TRAIL", ["PINE","NEEDLE","TRAIL","CONE","BARK","RESIN","CABIN","HIKE","STREAM","ROCK","FERN","QUIET"]),
    ("FROZEN POND", ["ICE","SKATE","FROST","STILL","REED","WINTER","COLD","CLEAR","BENCH","BREATH","SCARF","MOON"]),
    ("SPRING RAIN", ["DROP","BUD","FRESH","UMBRELLA","PUDDLE","ROBIN","WORM","GREEN","PETAL","RENEWAL","SOAK","JOY"]),
    ("AUTUMN ORCHARD", ["APPLE","BUSHEL","LADDER","RUSTIC","CIDER","CRISP","BRANCH","HARVEST","PIE","BARN","CRATE","ABUNDANT"]),
    ("LAVENDER FIELD", ["LAVENDER","PURPLE","ROW","BEE","SCENT","BREEZE","BUNDLE","DRY","HONEY","FRENCH","SACHET","PROVENCE"]),
    ("PEACEFUL POND", ["LILY","FROG","RIPPLE","REED","WILLOW","SHADE","TURTLE","DRAGON","STILL","REFLECT","PEACE","SILENCE"]),
    ("MOUNTAIN MEADOW", ["WILD","BLOOM","MEADOW","BREEZE","ELK","STREAM","ALPINE","RIDGE","BERRY","FERN","WIDE","SKY"]),
    ("SEASIDE TOWN", ["DOCK","PIER","SHELL","SAILBOAT","COTTAGE","SHOP","FISH","BAKERY","STREET","LANTERN","HARBOR","SEAGULL"]),
    ("FOREST CABIN", ["LOG","SMOKE","CHIMNEY","PORCH","ROCKER","DOG","KETTLE","TRAIL","WOLF","STAR","NIGHT","WARMTH"]),
    ("HERB GARDEN", ["BASIL","CHIVE","DILL","MINT","SAGE","THYME","PARSLEY","OREGANO","FENNEL","CILANTRO","TARRAGON","BAY"]),
    ("MORNING COFFEE", ["BREW","CUP","STEAM","BEAN","ROAST","CREAM","SUGAR","TOAST","PAGE","WINDOW","BIRD","RITUAL"]),
    ("NIGHT GARDEN", ["MOON","JASMINE","CRICKET","FIREFLY","BREEZE","STAR","OWL","SCENT","NIGHT","LANTERN","DEW","DREAM"]),
    ("COUNTRY LANE", ["FENCE","COW","BARN","HAYSTACK","WAGON","WILDFLOWER","BIRD","TREE","STONE","WALK","SUNNY","QUIET"]),
]


def make_grid(words):
    """Place words in 15x15 grid with horizontal/vertical/diagonal directions."""
    grid = [[None]*GRID_N for _ in range(GRID_N)]
    placed = []
    dirs = [(0,1),(1,0),(1,1),(-1,1),(0,-1),(-1,0),(-1,-1),(1,-1)]
    rng = random.Random(hash(tuple(words)) & 0xFFFFFFFF)
    for word in sorted(words, key=len, reverse=True):
        w = word.upper().replace(" ","")
        if len(w) > GRID_N:
            continue
        success = False
        for _ in range(400):
            dr, dc = rng.choice(dirs)
            r0 = rng.randint(0, GRID_N-1)
            c0 = rng.randint(0, GRID_N-1)
            r_end = r0 + dr*(len(w)-1)
            c_end = c0 + dc*(len(w)-1)
            if not (0 <= r_end < GRID_N and 0 <= c_end < GRID_N):
                continue
            ok = True
            for i, ch in enumerate(w):
                rr, cc = r0+dr*i, c0+dc*i
                if grid[rr][cc] is not None and grid[rr][cc] != ch:
                    ok = False; break
            if not ok:
                continue
            for i, ch in enumerate(w):
                rr, cc = r0+dr*i, c0+dc*i
                grid[rr][cc] = ch
            placed.append((word, r0, c0, dr, dc))
            success = True
            break
    # fill blanks
    for r in range(GRID_N):
        for c in range(GRID_N):
            if grid[r][c] is None:
                grid[r][c] = rng.choice(string.ascii_uppercase)
    return grid, placed


def draw_cover_page(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    cx = W/2
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(cx, H*0.74, "LARGE PRINT EDITION")
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(cx, H*0.62, "WORD SEARCH")
    c.drawCentredString(cx, H*0.56, "FOR SENIORS")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(GOLD)
    c.drawCentredString(cx, H*0.47, "Calming Nature Edition")
    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#BDC3C7"))
    c.drawCentredString(cx, H*0.38, "50 Themed Puzzles")
    c.drawCentredString(cx, H*0.355, "Large 15x15 Grid - Easy on the Eyes")
    c.drawCentredString(cx, H*0.33, "Garden, Forest, Beach, Mountain & More")
    c.drawCentredString(cx, H*0.305, "Complete Answer Key Included")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#7F8C8D"))
    c.drawCentredString(cx, M+15, "Deokgu Studio")
    c.showPage()


def draw_instructions(c):
    y = H - M - 0.2*inch
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, y, "How to Play")
    y -= 50
    c.setFont("Helvetica", 14)
    c.setFillColor(TEXT)
    lines = [
        "Welcome to Calming Nature Word Search!",
        "",
        "Each puzzle has a list of words to find in the grid.",
        "Words can run in 8 directions:",
        "",
        "  - Left to right    - Right to left",
        "  - Top to bottom    - Bottom to top",
        "  - And four diagonals",
        "",
        "Circle each word as you find it.",
        "Take your time - there is no rush.",
        "",
        "All answers are at the back of the book.",
        "",
        "These puzzles are designed to relax the mind",
        "and gently exercise memory and attention.",
        "",
        "Enjoy the calm of nature, one word at a time.",
    ]
    for line in lines:
        c.drawCentredString(W/2, y, line)
        y -= 22
    c.showPage()


def draw_puzzle_page(c, n, title, words, grid):
    # Header
    y = H - M
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(GRAY)
    c.drawString(M, y, f"PUZZLE {n}")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, y - 5, title)
    # Grid
    grid_size = W - 2*M
    cell = grid_size / GRID_N
    # ensure grid fits (height-wise)
    max_grid_h = H - 2*M - 3.0*inch
    if cell * GRID_N > max_grid_h:
        cell = max_grid_h / GRID_N
        grid_size = cell * GRID_N
    gx0 = (W - grid_size) / 2
    gy_top = y - 0.5*inch
    gy0 = gy_top - grid_size
    # cells
    c.setStrokeColor(HexColor("#BDC3C7"))
    c.setLineWidth(0.4)
    for i in range(GRID_N+1):
        c.line(gx0, gy0+i*cell, gx0+grid_size, gy0+i*cell)
        c.line(gx0+i*cell, gy0, gx0+i*cell, gy_top)
    # letters
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(TEXT)
    for r in range(GRID_N):
        for col in range(GRID_N):
            ch = grid[r][col]
            cx = gx0 + col*cell + cell/2
            cy = gy_top - r*cell - cell/2 - 5
            c.drawCentredString(cx, cy, ch)
    # word list
    list_y = gy0 - 0.35*inch
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(GREEN)
    c.drawCentredString(W/2, list_y, "FIND THESE WORDS:")
    list_y -= 18
    c.setFont("Helvetica", 12)
    c.setFillColor(TEXT)
    cols = 4
    col_w = (W - 2*M) / cols
    rows_needed = (len(words) + cols - 1) // cols
    for i, w in enumerate(words):
        r = i // cols
        col = i % cols
        x = M + col*col_w + col_w/2
        yy = list_y - r*16
        c.drawCentredString(x, yy, w)
    c.showPage()


def draw_answer_page(c, n, title, words, placed):
    y = H - M
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(GRAY)
    c.drawString(M, y, f"ANSWERS - PUZZLE {n}")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, y - 5, title)
    y -= 0.5*inch
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT)
    # Map word -> location string
    placement_map = {p[0]: (p[1], p[2], p[3], p[4]) for p in placed}
    cols = 2
    col_w = (W - 2*M) / cols
    for i, w in enumerate(words):
        r = i // cols
        col = i % cols
        x = M + col*col_w + 10
        yy = y - r*22
        if w in placement_map:
            r0, c0, dr, dc = placement_map[w]
            dir_name = {(0,1):"Right",(1,0):"Down",(1,1):"Down-Right",(-1,1):"Up-Right",
                        (0,-1):"Left",(-1,0):"Up",(-1,-1):"Up-Left",(1,-1):"Down-Left"}.get((dr,dc),"?")
            txt = f"{w}: row {r0+1}, col {c0+1} -> {dir_name}"
        else:
            txt = f"{w}: (skipped)"
        c.drawString(x, yy, txt)


def main():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    draw_cover_page(c)
    draw_instructions(c)
    grids = []
    for i, (title, words) in enumerate(PUZZLES, 1):
        grid, placed = make_grid(words)
        grids.append((i, title, words, grid, placed))
        draw_puzzle_page(c, i, title, words, grid)
    # answer key section header
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(W/2, H*0.55, "ANSWER KEY")
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H*0.48, "Solutions for All 50 Puzzles")
    c.showPage()
    # answers - 2 per page (top half + bottom half)
    pairs = [grids[i:i+2] for i in range(0, len(grids), 2)]
    for pair in pairs:
        # top
        i, title, words, grid, placed = pair[0]
        draw_answer_section(c, i, title, words, placed, y_anchor=H - M)
        if len(pair) == 2:
            i2, title2, words2, grid2, placed2 = pair[1]
            draw_answer_section(c, i2, title2, words2, placed2, y_anchor=H/2 - 0.2*inch)
        c.showPage()
    c.save()
    print(f"Saved {PDF_PATH}")


def draw_answer_section(c, n, title, words, placed, y_anchor):
    y = y_anchor
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(GRAY)
    c.drawString(M, y, f"ANSWERS - PUZZLE {n}")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, y - 5, title)
    y -= 0.35*inch
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT)
    placement_map = {p[0]: (p[1], p[2], p[3], p[4]) for p in placed}
    cols = 2
    col_w = (W - 2*M) / cols
    for i, w in enumerate(words):
        r = i // cols
        col = i % cols
        x = M + col*col_w + 10
        yy = y - r*16
        if w in placement_map:
            r0, c0, dr, dc = placement_map[w]
            dir_name = {(0,1):"Right",(1,0):"Down",(1,1):"Down-Right",(-1,1):"Up-Right",
                        (0,-1):"Left",(-1,0):"Up",(-1,-1):"Up-Left",(1,-1):"Down-Left"}.get((dr,dc),"?")
            txt = f"{w}: row {r0+1}, col {c0+1} -> {dir_name}"
        else:
            txt = f"{w}: (not placed)"
        c.drawString(x, yy, txt)


if __name__ == "__main__":
    main()
