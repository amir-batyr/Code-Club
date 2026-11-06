import turtle, random

STEP = 20
LIMIT = 280

screen = turtle.Screen()
screen.title("Snake")
screen.bgcolor("black")
screen.setup(600, 600)
screen.tracer(0)

# --- Game objects ---
head = turtle.Turtle("square")
head.color("lime")
head.penup()
head.direction = "stop"

food = turtle.Turtle("circle")
food.color("red")
food.penup()
food.goto(0, 100)

scoreboard = turtle.Turtle()
scoreboard.color("white")
scoreboard.penup()
scoreboard.hideturtle()
scoreboard.goto(0, 260)

segments = []
score = 0

# --- Steering ---
def go_up():
    if head.direction != "down": head.direction = "up"
def go_down():
    if head.direction != "up": head.direction = "down"
def go_left():
    if head.direction != "right": head.direction = "left"
def go_right():
    if head.direction != "left": head.direction = "right"

# --- Helpers ---
def move_head():
    if head.direction == "up":    head.sety(head.ycor() + STEP)
    if head.direction == "down":  head.sety(head.ycor() - STEP)
    if head.direction == "left":  head.setx(head.xcor() - STEP)
    if head.direction == "right": head.setx(head.xcor() + STEP)

def move_body():
    # Each segment jumps to where the one in front of it was.
    # We go from the tail forward so we don't overwrite positions too soon.
    for i in range(len(segments) - 1, 0, -1):
        segments[i].goto(segments[i - 1].pos())
    if segments:
        segments[0].goto(head.pos())

def add_segment():
    seg = turtle.Turtle("square")
    seg.color("green")
    seg.penup()
    segments.append(seg)

def move_food():
    food.goto(random.randrange(-LIMIT, LIMIT, STEP),
              random.randrange(-LIMIT, LIMIT, STEP))

def update_score():
    scoreboard.clear()
    scoreboard.write(f"Score: {score}", align="center",
                     font=("Arial", 18, "normal"))

def reset():
    global score
    head.goto(0, 0)
    head.direction = "stop"
    for seg in segments:
        seg.hideturtle()
    segments.clear()
    score = 0
    update_score()

# --- Game loop ---
def game_loop():
    global score

    if abs(head.xcor()) > LIMIT or abs(head.ycor()) > LIMIT:
        reset()

    if head.distance(food) < STEP:
        move_food()
        add_segment()
        score += 1
        update_score()

    move_body()
    move_head()

    if any(seg.distance(head) < STEP for seg in segments):
        reset()

    screen.update()
    screen.ontimer(game_loop, 100)

# --- Start ---
screen.listen()
screen.onkeypress(go_up, "Up")
screen.onkeypress(go_down, "Down")
screen.onkeypress(go_left, "Left")
screen.onkeypress(go_right, "Right")

update_score()
game_loop()
screen.mainloop()