import tkinter as tk
import random
import time
from PIL import Image, ImageTk
WIDTH = 400
HEIGHT = 400
CELL_SIZE = 20
INITIAL_DELAY = 100
SPEED_UP_DURATION=5
root = tk.Tk()
root.title("Змейка | Счёт: 0")
root.resizable(False, False)
main_frame = tk.Frame(root)
main_frame.pack()
canvas = tk.Canvas(main_frame, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
canvas.grid(row=0, column=0)
help_frame = tk.Frame(main_frame, width=200, bd=2, relief=tk.SUNKEN)
help_frame.grid(row=0, column=1, padx=10, sticky='ns')
help_label = tk.Label(help_frame, text=(
    "Яблоко Красное:\n"
    "  +1 очко\n\n"
    "Яблоко Синее:\n"
    "  +5 очков\n\n"
    "Яблоко Зеленое:\n"
    "  +1 очко + удлинение на 3 \n\n"
    "Сундук:\n"
    "  +2 очка + ускорение на 15 секунд"
), font=("Arial", 12), justify=tk.LEFT)
help_label.pack(padx=10, pady=10)

# Загрузка изображений
def load_and_resize_image(path, size):
    img = Image.open(path)
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS
    img = img.resize((size, size), resample)
    return ImageTk.PhotoImage(img)

apple_red_img = load_and_resize_image('red_apple.png', CELL_SIZE)
apple_blue_img = load_and_resize_image('blue_apple.png', CELL_SIZE)
apple_green_img = load_and_resize_image('green_apple.png', CELL_SIZE)
apple_normal_img = load_and_resize_image('apple.png', CELL_SIZE)
snake = [(100, 100), (90, 100), (80, 100)]
direction = "Right"
score = 0
game_over = False
game_started = False
current_delay = INITIAL_DELAY

food_red = None
food_blue = None
food_green = None
food_normal = None

speed_up_active = False
speed_up_end_time = None
def create_food(existing_positions):
    while True:
        x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        if (x, y) not in existing_positions:
            return (x, y)

def place_food():
    global food_red, food_blue, food_green, food_normal
    occupied = set(snake)
    food_red = create_food(occupied)
    occupied.add(food_red)
    food_blue = create_food(occupied)
    occupied.add(food_blue)
    food_green = create_food(occupied)
    occupied.add(food_green)
    food_normal = create_food(occupied)

def draw_food():
    if food_red:
        canvas.create_image(food_red[0] + CELL_SIZE // 2, food_red[1] + CELL_SIZE // 2, image=apple_red_img)
    if food_blue:
        canvas.create_image(food_blue[0] + CELL_SIZE // 2, food_blue[1] + CELL_SIZE // 2, image=apple_blue_img)
    if food_green:
        canvas.create_image(food_green[0] + CELL_SIZE // 2, food_green[1] + CELL_SIZE // 2, image=apple_green_img)
    if food_normal:
        canvas.create_image(food_normal[0] + CELL_SIZE // 2, food_normal[1] + CELL_SIZE // 2, image=apple_normal_img)

def draw_snake():
    for segment in snake:
        canvas.create_rectangle(segment[0], segment[1], segment[0] + CELL_SIZE, segment[1] + CELL_SIZE, fill="green", outline="darkgreen")

def move_snake():
    head_x, head_y = snake[0]
    if direction == "Up":
        new_head = (head_x, head_y - CELL_SIZE)
    elif direction == "Down":
        new_head = (head_x, head_y + CELL_SIZE)
    elif direction == "Left":
        new_head = (head_x - CELL_SIZE, head_y)
    elif direction == "Right":
        new_head = (head_x + CELL_SIZE, head_y)
    snake.insert(0, new_head)
def check_food_collision():
    global food_red, food_blue, food_green, food_normal, score, speed_up_active, speed_up_end_time
    reward = 0
    if snake[0] == food_red:
        score += 1
        reward = 1
        snake.extend([snake[-1]])
        place_food()
    elif snake[0] == food_blue:
        score += 5
        reward = 5
        snake.extend([snake[-1]] * 3)  # Повторяем последний сегмент 3 раза
        place_food()
    elif snake[0] == food_green:
        score += 1
        reward = 3
        snake.extend([snake[-1]])
        place_food()
    elif food_normal and snake[0] == food_normal:
        score += 1
        reward = 10
        start_speed_up()
        snake.extend([snake[-1]])
        place_food()
    return reward
def check_wall_collision():
    head_x, head_y = snake[0]
    return (head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT)
def check_self_collision():
    return snake[0] in snake[1:]
def end_game():
    global game_over
    game_over = True
    canvas.create_text(WIDTH//2, HEIGHT//2, text=f"Игра окончена! Счёт: {score}", fill="white", font=("Arial", 24))
def update_title():
    root.title(f"Змейка | Счёт: {score}")
def restart_game():
    global snake, direction, score, game_over, current_delay, speed_up_active, speed_up_end_time
    snake = [(100, 100), (90, 100), (80, 100)]
    direction = "Right"
    score = 0
    game_over = False
    current_delay = INITIAL_DELAY
    speed_up_active = False
    speed_up_end_time = None
    place_food()
    canvas.delete("all")
    draw_food()
    draw_snake()
    update_title()
def start_speed_up():
    global speed_up_active, speed_up_end_time, current_delay
    speed_up_active = True
    speed_up_end_time = time.time() + SPEED_UP_DURATION
    current_delay = max(20, current_delay // 2)
    update_countdown()
def update_countdown():
    if speed_up_active:
        remaining = int(speed_up_end_time - time.time()) + 1
        if remaining > 0:
            countdown_text = f"Ускорение: {remaining} сек"
            canvas.delete("countdown")
            canvas.create_text(WIDTH//2, HEIGHT//2 + 50, text=countdown_text, fill="yellow", font=("Arial", 14), tag="countdown")
            root.after(1000, update_countdown)
        else:
            end_speed_up()
def end_speed_up():
    global speed_up_active, current_delay
    speed_up_active = False
    current_delay = INITIAL_DELAY
    canvas.delete("countdown")
def game_loop():
    global snake, current_delay
    if game_over:
        return
    move_snake()
    if check_wall_collision() or check_self_collision():
        end_game()
        return
    reward = check_food_collision()
    if reward == 0:
        snake.pop()
    canvas.delete("all")
    draw_food()
    draw_snake()
    update_title()
    root.after(current_delay, game_loop)
def change_direction(new_direction):
    global direction
    opposites = {"Up":"Down", "Down":"Up", "Left":"Right", "Right":"Left"}
    if new_direction != opposites.get(direction):
        direction = new_direction
root.bind("<Up>", lambda event: change_direction("Up"))
root.bind("<Down>", lambda event: change_direction("Down"))
root.bind("<Left>", lambda event: change_direction("Left"))
root.bind("<Right>", lambda event: change_direction("Right"))

def start_game():
    global game_started
    if not game_started:
        game_started = True
        place_food()
        draw_food()
        draw_snake()
        game_loop()
start_button = tk.Button(root, text="Начать игру", command=start_game, font=("Arial", 14))
start_button.pack(pady=10)
update_title()
root.mainloop()