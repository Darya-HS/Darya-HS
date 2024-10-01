'''
The following changes have been applied:
    - The runner turtle was removed and replaced with a black rabbit (I don't see a point in adding a third player). The rabbit moves a lot faster now
      and is able to escape the boundaries of the screen, while the turtle cannot move outside the frame. This makes it a bit more difficult to win
    - The timer was added. The turtle has 15 seconds to catch up with the rabbit.
    - There are 5 rounds in total, the overall score is maintained. The overall winner is displayed according to the final score.
    - The title and the background color are added.
'''


import tkinter as tk
import turtle
import random
import math

class RunawayGame:
    def __init__(self, canvas, runner, chaser, catch_radius=50):
        self.canvas = canvas
        self.runner = runner
        self.chaser = chaser
        self.catch_radius2 = catch_radius**2
        self.time_left = 15
        self.game_over = False
        self.runner_score = 0
        self.chaser_score = 0
        self.rounds_played = 0
        self.total_rounds = 5
        self.timer_id = None


        self.runner.shape('rabbit')
        self.runner.color('black')
        self.runner.penup()
        self.chaser.shape('turtle')
        self.chaser.color('yellow')
        self.chaser.penup()

        self.drawer = turtle.RawTurtle(canvas)
        self.drawer.hideturtle()
        self.drawer.penup()
        
        self.timer_display = turtle.RawTurtle(canvas)
        self.timer_display.hideturtle()
        self.timer_display.penup()

        self.score_display = turtle.RawTurtle(canvas)
        self.score_display.hideturtle()
        self.score_display.penup()
        self.score_display.setpos(0, 250)

    def is_catched(self):
        p = self.runner.pos()
        q = self.chaser.pos()
        dx, dy = p[0] - q[0], p[1] - q[1]
        return dx**2 + dy**2 < self.catch_radius2

    def start(self, init_dist=400, ai_timer_msec=50):
        self.runner.clear()
        self.chaser.clear()
        self.drawer.clear()
        self.timer_display.clear()
        self.score_display.clear()
        
        self.runner.setpos((-init_dist / 2, 0))
        self.runner.setheading(0)
        self.chaser.setpos((+init_dist / 2, 0))
        self.chaser.setheading(180)
        self.ai_timer_msec = ai_timer_msec
        self.time_left = 15
        self.stop_timer()
        self.update_timer()
        self.canvas.ontimer(self.step, self.ai_timer_msec)

    def update_timer(self):
        if not self.game_over:
            self.timer_display.clear()
            self.timer_display.setpos(0, 300)
            self.timer_display.write(f'Time left: {self.time_left} seconds', align='center', font=('Arial', 16, 'normal'))
            if self.time_left > 0:
                self.time_left -= 1
                self.timer_id = self.canvas.ontimer(self.update_timer, 1000)
            else:
                self.end_game(False)

    def step(self):
        if not self.game_over:
            self.runner.run_ai(self.chaser.pos(), self.chaser.heading())
            self.chaser.run_ai(self.runner.pos(), self.runner.heading())
            if self.is_catched():
                self.end_game(True)
            else:
                self.drawer.clear()
                self.drawer.penup()
                self.drawer.setpos(-300, 300)
                self.canvas.ontimer(self.step, self.ai_timer_msec)

    def end_game(self, chaser_wins):
        self.game_over = True
        self.canvas.ontimer(lambda: self.stop_timer(), 0)
        self.drawer.clear()
        self.drawer.setpos(0, 0)
    
        if chaser_wins:
            self.chaser_score += 1
            self.drawer.write('Turtle caught the rabbit!', align='center', font=('Arial', 24, 'normal'))
        else:
            self.runner_score += 1
            self.drawer.write('Time\'s up! Rabbit ran away!', align='center', font=('Arial', 24, 'normal'))
    
        self.score_display.clear()
        self.score_display.write(f'Scores - Rabbit: {self.runner_score} | Turtle: {self.chaser_score}', align='center', font=('Arial', 16, 'normal'))
    
        self.rounds_played += 1
        
        if self.rounds_played < self.total_rounds:
            self.canvas.ontimer(self.prepare_next_round, 2000)
        else:
            self.display_final_winner()

            
    def stop_timer(self):
        if self.timer_id is not None:
            self.canvas.ontimer(lambda: None, self.timer_id)
            self.timer_id = None  # Reset timer ID
    
    def prepare_next_round(self):
        self.game_over = False
        self.stop_timer()
        self.start()
    
    def display_final_winner(self):
        self.drawer.clear()
        self.drawer.setpos(0, 0)
        
        if self.chaser_score > self.runner_score:
            self.drawer.write('Overall Winner: Turtle!', align='center', font=('Arial', 24, 'normal'))
        elif self.runner_score > self.chaser_score:
            self.drawer.write('Overall Winner: Rabbit!', align='center', font=('Arial', 24, 'normal'))
        else:
            self.drawer.write('Overall Result: It\'s a Tie!', align='center', font=('Arial', 24, 'normal'))

class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn
        self.screen_width = 350
        self.screen_height = 350
        
        canvas.onkeypress(lambda: self.move_within_bounds(self.forward, self.step_move), 'Up')
        canvas.onkeypress(lambda: self.move_within_bounds(self.backward, self.step_move), 'Down')
        canvas.onkeypress(lambda: self.left(self.step_turn), 'Left')
        canvas.onkeypress(lambda: self.right(self.step_turn), 'Right')
        canvas.listen()

    def move_within_bounds(self, move_func, step):
        initial_pos = self.pos()
        move_func(step)
        new_pos = self.pos()
        
        if not (-self.screen_width <= new_pos[0] <= self.screen_width and -self.screen_height <= new_pos[1] <= self.screen_height):
            self.setpos(initial_pos)

    def run_ai(self, opp_pos, opp_heading):
        pass

class RandomMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=50, step_turn=20):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn

    def run_ai(self, opp_pos, opp_heading):
        mode = random.randint(0, 2)
        if mode == 0:
            self.forward(self.step_move)
        elif mode == 1:
            self.left(self.step_turn)
        elif mode == 2:
            self.right(self.step_turn)

def create_rabbit_shape():
    shape = []
    
    for angle in range(0, 360, 10):
        x = 8 * math.cos(math.radians(angle))
        y = 12 * math.sin(math.radians(angle)) - 5
        shape.append((x, y))
    
    for angle in range(0, 360, 10):
        x = 6 * math.cos(math.radians(angle))
        y = 6 * math.sin(math.radians(angle)) + 12
        shape.append((x, y))
    
    shape.extend([
        (-5, 18), (-5, 26), (-2, 28), (0, 18),
        (5, 18), (5, 26), (2, 28), (0, 18)
    ])
    
    return tuple(shape)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Rabbit Runaway")
    canvas = tk.Canvas(root, width=700, height=700)
    canvas.pack()
    screen = turtle.TurtleScreen(canvas)
    screen.bgcolor('lightgreen')

    rabbit_shape = create_rabbit_shape()
    screen.register_shape('rabbit', rabbit_shape)

    runner = RandomMover(screen)
    chaser = ManualMover(screen)
    game = RunawayGame(screen, runner, chaser)
    game.start()
    screen.mainloop()
