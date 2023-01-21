import pygame
from pygame.sprite import Sprite, Group
from pygame.rect import Rect
from pygame.surface import Surface
from typing import Dict

# from https://opengameart.org/content/asteroids-vector-style-sprites
filename = "asteroids-2x.png"

bigAsteroid1 = Rect(0, 0, 160, 160)
bigAsteroid2 = Rect(160, 0, 160, 160)
bigAsteroid3 = Rect(320, 0, 160, 160)
asteroid1 = Rect(0, 160, 96, 96)
asteroid2 = Rect(96, 160, 96, 96)
asteroid3 = Rect(192, 160, 96, 96)
ufo = Rect(288 + 16 * 8, 160, 96, 80)
smAsteroid1 = Rect(0, 160 + 96, 64, 64)
smAsteroid2 = Rect(64, 160 + 96, 64, 64)
smAsteroid3 = Rect(128, 160 + 96, 64, 64)
ship = Rect(128 + 64, 160 + 96, 96, 64)
shipThrust = Rect(128 + 64 + 96, 160 + 96, 96, 64)
bullet = Rect(28 * 16, 160 + 96 + 32, 32, 32)
bigBullet = Rect(30 * 16, 160 + 96 + 32, 32, 32)

# constants
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

WIDTH = 640
HEIGHT = 480

if __name__ == "__main__":
    pygame.init()
    size = (WIDTH, HEIGHT)
    window = pygame.display.set_mode(size)


# inspired by https://ehmatthes.github.io/pcc_2e/beyond_pcc/pygame_sprite_sheets/
class SpriteSheet:

    def __init__(self):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
            self.rectDict = None
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectIn: Rect) -> Surface:
        rect = Rect(rectIn)
        image = Surface(rect.size).convert_alpha()
        image.fill((0, 0, 0, 0))
        image.blit(self.sheet, (0, 0), rect)
        return image

    def getSpriteRects(self) -> Dict[str, Rect]:
        if self.rectDict is None:
            spriteRects = {
                "bigAsteroid1": bigAsteroid1,
                "bigAsteroid2": bigAsteroid2,
                "bigAsteroid3": bigAsteroid3,
                "asteroid1": asteroid1,
                "asteroid2": asteroid2,
                "asteroid3": asteroid3,
                "ufo": ufo,
                "smAsteroid1": smAsteroid1,
                "smAsteroid2": smAsteroid2,
                "smAsteroid3": smAsteroid3,
                "ship": ship,
                "shipThrust": shipThrust,
                "bullet": bullet,
                "bigBullet": bigBullet,
            }
            self.rectDict = spriteRects.copy()
        return self.rectDict

    def getSpriteRect(self, name: str) -> Rect:
        if self.rectDict is None:
            self.rectDict = self.getSpriteRects()
        return self.rectDict[name]

    def testSpriteSheet(self, window: Surface) -> None:
        tempGroup = Group()
        testingCurrentX = 10
        testingCurrentY = 10
        largestSpriteHeight = -1

        for key in self.getSpriteRects():
            tempImgRect = self.getSpriteRect(key)

            # if the sprite will be drawn outside of the screen move it
            # to the next row down by the largest sprite in the current row
            if testingCurrentX + tempImgRect.width > window.get_width():
                testingCurrentX = 10
                testingCurrentY += largestSpriteHeight + 1
                largestSpriteHeight = -1

            # make a temporary sprite for fun happy test rendering
            # for actual game use, a subclass would be better
            tempSprite = Sprite()
            tempSprite.rect = Rect(testingCurrentX, testingCurrentY,
                                   tempImgRect.width, tempImgRect.height)
            tempSprite.image = self.image_at(tempImgRect)

            tempSprite.mask = pygame.mask.from_surface(tempSprite.image, 240)
            # 240 is a good value to ignore most of the glow effect and have a collision map

            # check if this sprite is bigger than any we've seen so far, if so remember that
            largestSpriteHeight = max(
                tempSprite.image.get_bounding_rect().height,
                largestSpriteHeight)
            tempGroup.add(tempSprite)

            #draw image surface size
            my_image_rect = tempSprite.image.get_rect(
                center=tempSprite.rect.center)
            pygame.draw.rect(window, (0, 255, 0), my_image_rect, 3)

            #draw bounding box of image size
            bounding_rect = tempSprite.image.get_bounding_rect()
            bounding_rect.move_ip(my_image_rect.topleft)
            pygame.draw.rect(window, (255, 0, 0), bounding_rect, 3)

            #draw collision mask of image
            maskCopy = tempSprite.mask.to_surface(surface=tempSprite.image,
                                                  setcolor=(0, 0, 255, 255),
                                                  unsetcolor=None).copy()
            window.blit(maskCopy, tempSprite.rect.topleft)

            #move the X for the next image
            testingCurrentX += tempImgRect.width + 1

        Group.draw(tempGroup, window)


if __name__ == "__main__":
    import sys

    spriteSheet = SpriteSheet()

    size = (WIDTH, HEIGHT)
    window = pygame.display.set_mode(size)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # main drawing loop
        window.fill(BLACK)

        # Draw all sprites
        spriteSheet.testSpriteSheet(window)
        pygame.display.flip()

        # render tick
        clock.tick(60)

    pygame.quit()
    sys.exit()
