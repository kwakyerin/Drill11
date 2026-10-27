import time
from math import pi

from pico2d import load_image
from transitions import Machine

class Boy:
    IDLE = 'IDLE'
    RUN = 'RUN'
    SLEEP = 'SLEEP'

    SCREEN_WIDTH = 800
    HALF_WIDTH = 50
    RUN_SPEED = 5
    SLEEP_OFFSET_Y = 10

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.pressed_directions = []
        self.idle_started_at = time.monotonic()
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=[self.IDLE, self.RUN, self.SLEEP],
            initial=self.IDLE,
            auto_transitions=False,
            transitions=[
                {'trigger': 'sleep', 'source': self.IDLE, 'dest': self.SLEEP},
                {
                    'trigger': 'run',
                    'source': [self.IDLE, self.SLEEP],
                    'dest': self.RUN,
                },
                {
                    'trigger': 'stop_run',
                    'source': self.RUN,
                    'dest': self.IDLE,
                    'after': 'reset_idle_timer',
                },
                {
                    'trigger': 'wake',
                    'source': self.SLEEP,
                    'dest': self.IDLE,
                    'after': 'reset_idle_timer',
                },
            ],
        )

    def update(self):
        if self.state == self.IDLE:
            if time.monotonic() - self.idle_started_at >= 5:
                self.sleep()
            else:
                self.frame = (self.frame + 1) % 8
        elif self.state == self.RUN:
            self.frame = (self.frame + 1) % 8
            self.x = min(
                max(
                    self.x + self.face_dir * self.RUN_SPEED,
                    self.HALF_WIDTH,
                ),
                self.SCREEN_WIDTH - self.HALF_WIDTH,
            )

    def reset_idle_timer(self):
        self.idle_started_at = time.monotonic()

    def press_direction(self, direction):
        if direction in self.pressed_directions:
            self.pressed_directions.remove(direction)
        self.pressed_directions.append(direction)
        self.face_dir = direction

        if self.state in (self.IDLE, self.SLEEP):
            self.frame = 0
            self.run()

    def release_direction(self, direction):
        if direction not in self.pressed_directions:
            return

        self.pressed_directions.remove(direction)
        if self.state != self.RUN:
            return

        if self.pressed_directions:
            self.face_dir = self.pressed_directions[-1]
        else:
            self.stop_run()

    def draw(self):
        if self.state == self.SLEEP:
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(
                0,
                row,
                100,
                100,
                -pi / 2,
                '',
                self.x,
                self.y - self.SLEEP_OFFSET_Y,
                100,
                100,
            )
            return

        if self.state == self.RUN:
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
            return

        if self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)