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

    def change_speed(self, dx, dy):
        self.horizontal_speed += dx

    def move(self, platforms):
        old_horizontal_pos = self.rect.left
        self.rect.left += self.horizontal_speed
        if pygame.sprite.spritecollideany(self, platforms) is not None:
            self.rect.left = old_horizontal_pos

    def jump(self):
        pass


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
    platforms = [[0, window_height - 20,
                  window_width, 15, platform_color],
                 [window_width - 200, window_height - 60,
                  70, 30, platform_color]]

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
                    self.player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.change_speed(5, 0)
                if event.key == pygame.K_RIGHT:
                    self.player.change_speed(-5, 0)

        self.player.move(self.platforms_group)


def main():
    game = Game()

    while not game.done:
        game.process_events()

        game.canvas.fill("black")
        game.platforms_group.draw(game.canvas)
        game.player_group.draw(game.canvas)

        pygame.display.update()
        game.clock.tick(game.fps)

    pygame.quit()


if __name__ == "__main__":
    sys.stdin = open(path.join("lec_26", "email.txt"))
    main()
