"""Tank steering sandbox — project notes for future maintainers/agents.

Keep exactly four files in this folder: server.py, index.html, app.js, style.css.
Run `python server.py`, then open http://127.0.0.1:8000 in a desktop browser.
Standard-library Python only; the browser needs its Gamepad API for USB input.

Purpose: try steering algorithms for a battlebot in a *simulation*, beginning with
independent left/right vertical-stick control. No mixing, FPV-style rates, real
motors, serial connection, transmitter configuration, or safety interlocks for
physical hardware have been implemented. Do not use this as motor-control code.

Data path: RadioMaster Pocket ELRS in USB Joystick mode -> browser Gamepad API
(or W/S and Up/Down keyboard) -> app.js normalizes four stick axes to 0..100
(50=center) -> POST /input -> process_input() -> steering(channels) -> left
and right commands in -100..100 -> step() differential-drive physics ->
JSON state -> app.js draws the SVG bot and statistics in index.html.
GET /state reads/advances physics; POST /reset restores pose, not radio mapping.
style.css keeps the arena square and the controls outside it.

EDITING GUIDE: Implement experimental steering in steering(channels) below.
It is called by process_input(); change the function body, not the HTTP server.
If adding helper functions, define them above steering() and call them there.
Change joystick-axis choices/inversion in the page, not in steering(). The
initial CH3/CH2 guesses depend on the user's EdgeTX model and USB settings;
verify via the on-screen raw axes. There is no calibration/persistence yet.

Caveats: a non-centering throttle stick can immediately command motion in this
simulation. On missed browser updates motor commands stop after 0.3 seconds.
State is global, single-simulation, in-memory, and not designed for multiple
tabs/users; resetting or refreshing the page does not configure the radio.
The server binds to 127.0.0.1 only. Test mappings and behavior before ever
adapting anything for a physical robot.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import math
import time

ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8000
WORLD = 900.0
BOT_WIDTH, BOT_LENGTH = 96.0, 62.0
MAX_SPEED = 250.0       # pixels/second at 100% motor command
WHEEL_SPACING = 78.0    # pixels between the wheel tracks
INPUT_TIMEOUT = 0.3     # stop if browser stops sending inputs

state = {
    "x": 260.0, "y": 250.0, "heading": 0.0,
    "left_motor": 0.0, "right_motor": 0.0,
    "channels": {"left_x": 50.0, "left_y": 50.0,
                 "right_x": 50.0, "right_y": 50.0},
    "active": False, "source": "none",
}
last_input = 0.0
last_step = time.monotonic()


def clamp(value, low, high):
    return max(low, min(high, value))


# ================================================================
# YOUR STEERING EXPERIMENTS GO HERE.
# Inputs: four stick channels, each 0..100 (50 = center).
# Outputs: (left_motor, right_motor), each -100..100.
# Positive = forward, negative = reverse. This first version uses
# only the two vertical axes: direct, traditional tank steering.
# To try a new method later, replace this function's body ONLY.
# process_input() below is where this function is CALLED.
# ================================================================
def steering(channels):
    MAXRATE = 100
    CENTERSENSITIVITY = 30
    EXPO = 0.7
    left_x = channels["left_x"]
    left_y = channels["left_y"]
    right_x = channels["right_x"]
    right_y = channels["right_y"]


    x = right_x
    y = right_y
    x = RateProfile(x, MAXRATE, CENTERSENSITIVITY, EXPO)
    y = RateProfile(y, MAXRATE, CENTERSENSITIVITY, EXPO)

    left, right = mvmt(x, y)

    

    # Outputs below
    # left, right: (0.0, 100.0)
    left = (left - 50.0) * 2
    right = (right - 50.0) * 2
    return left, right

def RateProfile(inputValue: float, maxRate: float, centerSensitivity: float, expo: float) -> float:
# 
#     /*
#     Applies a rate profile to an input value.
#     Args:
#         inputValue: input value range [0.0, 100.0]
#     Returns:
#         output in range [0.0, 100.0]

#     Function:
#     https://www.desmos.com/calculator/xuywkbmlsd
#     y=C*x+(M-C)*abs(x)*(E*x^5+(1-E)*x)
#     */
    expoMult = 0
    output = 0

    # // keeps value of expo in range [0.0, 1.0]
    if((expo < 0) or (expo > 1)):
        if(expo < 0):
            expo = 0
        
        if(expo > 1):
            expo = 1
        
    

    # // keeps value of maxRate, inputValue, and centerSensitivity in range [0.0, 100.0]
    if((maxRate < 0) or (maxRate > 100)):
        if(maxRate < 0):
            maxRate = 0
        
        if(maxRate > 100):
            maxRate = 100
        
    
    if((inputValue < 0) or (inputValue > 100)):
        if (inputValue < 0):
            inputValue = 0
        
        if (inputValue > 100):
            inputValue = 100
        
    
    if((centerSensitivity < 0) or (centerSensitivity > 100)):
        if (centerSensitivity < 0):
            centerSensitivity = 0
        
        if (centerSensitivity > 100):
            centerSensitivity = 100;
        
    

    # // Transforms input to be in range of [-1.0, 1.0]
    inputValue = (inputValue - 50) / 50
    
    expoMult = (expo * (inputValue**5) + (1-expo)*inputValue)
    output = (centerSensitivity* inputValue) +(maxRate - centerSensitivity)*abs(inputValue)*expoMult
    # // output is now in a range -100, 100

    # //center output at 50
    output = (output + 100)/2
    return output

def mvmt(x: float, y: float) -> tuple:
    """
    Args:
        x (float): x input in range [0.0, 100.0]
        y (float): y input in range [0.0, 100.0]
    Returns:
        (tuple) (left, right): left and right motor commands in range [-1, 1]
    """
    x = motor_to_working_values(x)
    y = motor_to_working_values(y)

    character = None
    if abs(x) >= abs(y):
        character = "more_horizontal"
    elif abs(y) > abs(x):
        character = "more_vertical"
    # elif abs(x) == abs(y):
    #     character = "diagonal"
    else: 
        assert False

    if x == y == 0.0:
        return (50.0, 50.0)
    
    # direction = (int(x//abs(x)), int(y//abs(y)))
    if x != 0:
        dx = int(x//abs(x))
    else:
        dx = 0
    if y != 0:
        dy = int(y//abs(y))
    else:
        dy = 0
    direction = (dx, dy)

    # print(f"dir: {direction}")
    corner = vec(direction)
    # print(f"corner: {corner}")

    # if character == "diagonal":
    #     return (x, y)

    if character == "more_vertical":
        side = vec((0, direction[1]))
    elif character == "more_horizontal":
        side = vec((direction[0], 0))
    else:
        assert False
    # print(f"side: {side}")

    # normalizing values and stuff to get standard right triangle setup
    if character == "more_horizontal":
        a = abs(x)
        b = abs(y)
    elif character == "more_vertical":
        a = abs(y)
        b = abs(x)
    else:
        assert False

    side_pct = a - b
    corner_pct = b
    # print(f"side_pct: {side_pct}, corner_pct: {corner_pct}")

    left = side[0]*side_pct + corner[0]*corner_pct
    right = side[1]*side_pct + corner[1]*corner_pct

    # print(f"left: {left}, right: {right}")
    left = working_to_motor_values(left)
    right = working_to_motor_values(right)
    return left, right
    
def vec(input: tuple) -> tuple:
    x = input[0]
    y = input[1]
    vector_table = [[(0, 1), (1, 1), (1, 0)], 
                    [(-1, 1), (0, 0), (1, -1)], 
                    [(-1, 0), (-1, -1), (0, -1)]]
    return vector_table[(-y)+1][x+1]

def motor_to_working_values(input: float) -> float:
    # maps values in range [0.0, 100.0] to range [-1.0, 1.0]
    return (input-50)/50

def working_to_motor_values(input: float) -> float:
    # maps values in range [-1.0, 1.0] to range [0.0, 100.0]
    return (input*50) + 50

# END USER SPACE
def process_input(payload):
    """Receive normalized browser channels, then call steering()."""
    global last_input
    channels = payload.get("channels", {})
    for name in state["channels"]:
        value = float(channels.get(name, 50.0))
        if not math.isfinite(value):
            raise ValueError("Channels must be finite numbers")
        state["channels"][name] = clamp(value, 0.0, 100.0)

    state["active"] = payload.get("active") is True
    state["source"] = str(payload.get("source", "none"))[:32]
    last_input = time.monotonic()
    if state["active"]:
        left, right = steering(state["channels"])  # YOUR FUNCTION IS CALLED HERE
        state["left_motor"] = clamp(float(left), -100.0, 100.0)
        state["right_motor"] = clamp(float(right), -100.0, 100.0)
    else:
        state["left_motor"] = state["right_motor"] = 0.0


def step():
    """Move a differential-drive rectangle using the latest commands."""
    global last_step
    now = time.monotonic()
    dt = clamp(now - last_step, 0.0, 0.05)
    last_step = now
    if now - last_input > INPUT_TIMEOUT:
        state["active"] = False
        state["left_motor"] = state["right_motor"] = 0.0

    left_speed = state["left_motor"] / 100.0 * MAX_SPEED
    right_speed = state["right_motor"] / 100.0 * MAX_SPEED
    turn = (left_speed - right_speed) / WHEEL_SPACING * dt
    # Midpoint integration keeps curved paths visually smooth.
    mid = state["heading"] + turn / 2.0
    travel = (left_speed + right_speed) / 2.0 * dt
    state["x"] += math.sin(mid) * travel
    state["y"] -= math.cos(mid) * travel
    state["heading"] = (state["heading"] + turn) % (2.0 * math.pi)
    # Keep all four rotated corners inside the square.
    a = state["heading"]
    margin_x = abs(math.cos(a)) * BOT_WIDTH / 2 + abs(math.sin(a)) * BOT_LENGTH / 2
    margin_y = abs(math.sin(a)) * BOT_WIDTH / 2 + abs(math.cos(a)) * BOT_LENGTH / 2
    state["x"] = clamp(state["x"], margin_x, WORLD - margin_x)
    state["y"] = clamp(state["y"], margin_y, WORLD - margin_y)


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body, content_type="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/state":
            step()
            return self.reply(200, json.dumps(state).encode())
        files = {"/": ("index.html", "text/html; charset=utf-8"),
                 "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                 "/style.css": ("style.css", "text/css; charset=utf-8")}
        if self.path not in files:
            return self.reply(404, b"Not found", "text/plain")
        filename, content_type = files[self.path]
        try:
            self.reply(200, (ROOT / filename).read_bytes(), content_type)
        except FileNotFoundError:
            self.reply(404, b"Missing project file", "text/plain")

    def do_POST(self):
        if self.path not in ("/input", "/reset"):
            return self.reply(404, b"Not found", "text/plain")
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 4096:
                raise ValueError("Request too large")
            payload = json.loads(self.rfile.read(size)) if size else {}
            step()  # advance old commands before applying new ones
            if self.path == "/reset":
                state.update(x=260.0, y=250.0, heading=0.0)
            else:
                process_input(payload)
            self.reply(200, json.dumps(state).encode())
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            self.reply(400, json.dumps({"error": str(error)}).encode())


if __name__ == "__main__":
    print(f"Tank simulator: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop. Simulation only; no hardware motor output.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
