import pygame
import sys
from os import path


class Player(pygame.sprite.Sprite):

    def __init__(self, width, height, left, top, color):
        super().__init__()

        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.rect.left = left
        self.rect.top = top
        self.horizontal_speed = 0
        self.vertical_speed = 0

    def change_speed(self, dx, dy):
        self.horizontal_speed += dx
        self.vertical_speed += dy

    def gravity(self, platforms):
        if self.vertical_speed != 0:
            self.vertical_speed += 0.37
        else:
            self.rect.top += 2
            if pygame.sprite.spritecollide(self, platforms, False):
                self.rect.top -= 2

    def landscape_move(self, platforms, direction):
        if self.horizontal_speed != 0:
            if direction == "left":
                for platform in platforms:
                    platform.rect.left -= self.horizontal_speed

                horizontal_collide_list = (
                    pygame.sprite.spritecollide(self, platforms, False))
                for platform in horizontal_collide_list:
                    self.rect.left = platform.rect.right
                    self.horizontal_speed = 0

            elif direction == "right":
                for platform in platforms:
                    platform.rect.left -= self.horizontal_speed

                horizontal_collide_list = (
                    pygame.sprite.spritecollide(self, platforms, False))
                for platform in horizontal_collide_list:
                    self.rect.right = platform.rect.left
                    self.horizontal_speed = 0

    def move(self, platforms, game):
        '''
        If player.rect.left = left border and we are moving to the left
        we move to the right platforms, not the player.
        If player.rect.left = right border and we are moving to the right
        we move to the left platforms, not the player.
        In other cases we move player to the playef.horisontal_speed.

        FIXME need to delete a possibility to make a jump during
        player slide from platform while he is in the air.
        '''
        left_border = 50
        right_border = game.window_width - self.rect.width - 50
        self.gravity(platforms)
        if (self.rect.left <= left_border and
                self.horizontal_speed < 0):
            self.landscape_move(platforms, "left")
        elif (self.rect.left >= right_border and
              self.horizontal_speed > 0):
            self.landscape_move(platforms, "right")
        else:
            self.rect.left += self.horizontal_speed
            horizontal_collide_list = (
                    pygame.sprite.spritecollide(self, platforms, False))

            for platform in horizontal_collide_list:
                if self.horizontal_speed > 0:
                    self.rect.right = platform.rect.left
                else:
                    self.rect.left = platform.rect.right
                self.horizontal_speed = 0

        self.rect.top += self.vertical_speed
        vertical_collide_list = (
                pygame.sprite.spritecollide(self, platforms, False))

        for platform in vertical_collide_list:
            if self.vertical_speed > 0:
                self.rect.bottom = platform.rect.top
            else:
                self.rect.top = platform.rect.bottom
            self.vertical_speed = 0

    def jump(self):
        self.change_speed(0, -10)


class Platform(pygame.sprite.Sprite):

    def __init__(self, left, top, width, height, color):
        '''
        platform format: left, top, width, height, color
        '''
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top


class MovingPlatform(Platform):

    def __init__(self, left, top, width, height, color,
                 left_bound, right_bound, top_bound, bottom_bound):
        '''
        first swing always from left to the right and from the top to the
        bottom.
        Those are two flags which said are we swinging in horizontal and
        vertical space part
        self.horizontal = False
        self.vetrical = False

        '''
        super().__init__(left, top, width, height, color)
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.top_bound = top_bound
        self.bottom_bound = bottom_bound
        self.horizontal_step = {"normal": 1, "reverse": -1}
        self.verical_step = {"normal": 1, "reverse": -1}
        self.horizontal_direction = "normal"
        self.vertical_direction = "normal"
        # self.speed = [0, 0]
        self.horizontal = False
        self.vetrical = False
        if self.left_bound != self.right_bound:
            # self.speed[0] = 1
            self.horizontal = True
        if self.top_bound != self.bottom_bound:
            # self.speed[1] = 1
            self.vetrical = True

    def swing(self):
        if self.horizontal:
            if self.rect.left < self.left_bound:
                self.horizontal_direction = "normal"
            elif self.rect.left > self.right_bound:
                self.horizontal_direction = "reverse"
            # if self.directions_index == "normal":
            self.rect.left += self.horizontal_step[self.horizontal_direction]
        if self.vetrical:
            if self.rect.top < self.top_bound:
                self.vertical_direction = "normal"
            elif self.rect.top > self.bottom_bound:
                self.vertical_direction = "reverse"
            self.rect.top += self.verical_step[self.vertical_direction]


class Game():
    window_width = 700
    window_height = 650
    player_height = 30
    player_width = 15
    player_top = window_height - 20 - player_height
    player_left = 60
    player_color = "white"
    fps = 60
    done = False
    platform_color = pygame.Color(4, 255, 252)
    # platform format: left, top, width, height, color
    platforms = [[-500, window_height - 20,
                  window_width * 2, 15, platform_color],
                 [window_width - 200, window_height - 60,
                  150, 30, platform_color],
                 [window_width - 400, window_height - 150,
                  150, 30, platform_color],
                 [-300, window_height - 60,
                  150, 30, platform_color], ]
    moving_platforms = [[300, window_height - 80,
                        150, 30, platform_color,
                        0, 0, 120, 450],
                        [200, window_height - 80,
                        150, 30, platform_color,
                        20, 120, 0, 0], ]

    def __init__(self):
        self.clock = pygame.time.Clock()
        window_size = [self.window_width, self.window_height]
        self.canvas = pygame.display.set_mode(window_size)
        self.player_group = pygame.sprite.Group()
        self.platforms_group = pygame.sprite.Group()
        self.player = Player(self.player_width, self.player_height,
                             self.player_left, self.player_top,
                             self.player_color)
        self.player_group.add(self.player)
        for platform in self.platforms:
            self.platforms_group.add(Platform(*platform))

        self.moving_platforms_group = pygame.sprite.Group()
        for moving_platform in self.moving_platforms:
            self.moving_platforms_group.add(MovingPlatform(*moving_platform))

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.change_speed(-5, 0)
                if event.key == pygame.K_RIGHT:
                    self.player.change_speed(5, 0)
                if event.key == pygame.K_UP:
                    if self.player.vertical_speed == 0:
                        self.player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    if self.player.horizontal_speed != 0:
                        self.player.change_speed(5, 0)
                if event.key == pygame.K_RIGHT:
                    if self.player.horizontal_speed != 0:
                        self.player.change_speed(-5, 0)

        self.player.move(self.platforms_group, self)
        for moving_platform in self.moving_platforms_group:
            moving_platform.swing()


def main():
    game = Game()

    while not game.done:
        game.process_events()

        game.canvas.fill("black")
        game.platforms_group.draw(game.canvas)
        game.player_group.draw(game.canvas)
        game.moving_platforms_group.draw(game.canvas)

        pygame.display.update()
        game.clock.tick(game.fps)

    pygame.quit()


if __name__ == "__main__":
    sys.stdin = open(path.join("lec_26", "email.txt"))
    main()
