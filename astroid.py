import pygame
from pygame.sprite import Sprite, Group
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.math import Vector2
from sprites import SpriteSheet
from typing import List
import random

import sys, math

# constants
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

WIDTH = 1280
HEIGHT = 720

if __name__ == "__main__":
    pygame.init()
    size = (WIDTH, HEIGHT)
    window = pygame.display.set_mode(size)

spriteSheet = SpriteSheet()


class PhysicsSprite(Sprite):
    def __init__(self, initialX, initialY, initialDx, initialDy):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)
        self.vector = Vector2(initialDx, initialDy)
        self.x = initialX
        self.y = initialY
        self.angle = 90

    def update(self, *args, **kwargs) -> None:
        if self.vector and self.vector.magnitude() < 0.29:
            self.vector.update((0,0))

        self.x += self.vector[0]
        self.y += self.vector[1]

        if self.rect is not None:
            #screen wrapping logic
            if self.rect.left > WIDTH:
                self.x = 0
            elif self.rect.right < 0:
                self.x = WIDTH
            if self.rect.top > HEIGHT:
                self.y = 0
            elif self.rect.bottom < 0:
                self.y = HEIGHT

            self.rect.centerx = self.x
            self.rect.centery = self.y

            if self.image is not None and self.originalImage is not None:
                self.image = pygame.transform.rotate(self.originalImage.copy(), self.angle)
                image_center = self.image.get_rect(center = (self.x, self.y)).center
                self.rect = self.image.get_rect(center = image_center)
                self.mask = pygame.mask.from_surface(self.image, 240)

                # collidedSprites = pygame.sprite.spritecollide(self, args, False, collided=pygame.sprite.collide_mask)
                # if len(collidedSprites) > 0:
                #     self.on_collision(collidedSprites)

        return super().update(*args, **kwargs)

    def rotate(self, angle: float) -> None:
        self.angle += angle

    def process_single_collision(sprite, collided_sprite):
        #find collision point

        if False:#hasattr(sprite, 'radius'):
            collision_point = Vector2(sprite.x, sprite.y) - Vector2(collided_sprite.x, collided_sprite.y)
            collision_point.normalize_ip()
            collision_point *= sprite.radius
            collision_mask_point = Vector2(sprite.image) + collision_point
            pygame.draw.circle(sprite.image, (255, 0, 0), collision_point, 5)
            collision_point_normal = collision_point.rotate(180)
            #use reflect to bounce vector off of rotated collision point
            if sprite.vector and sprite.vector.magnitude() != 0:
                pygame.math.Vector2.reflect_ip(sprite.vector, collision_point_normal)
            # sprite_position = Vector2(sprite.x, sprite.y)
            # collided_sprite_position = Vector2(collided_sprite.x, collided_sprite.y)
            # distance = sprite_position.distance_to(collided_sprite_position)
            # return distance < sprite.radius + collided_sprite.radius
        else:
            collision_mask_point = pygame.sprite.collide_mask(sprite, collided_sprite)
            if collision_mask_point is None:
                return

            count = 1
            touching = True
            touching_collision_mask_point = Vector2(collision_mask_point)
            #touching = collision_mask_point is not None
            while touching:
                collision_mask_rect = sprite.mask.to_surface().get_bounding_rect()
                touching_collision_point = Vector2(collision_mask_rect.center) - Vector2(touching_collision_mask_point)
                pygame.math.Vector2.normalize_ip(touching_collision_point)
                #pygame.math.Vector2.rotate_ip(touching_collision_point, 180)
                widest_point = count#max(collision_mask_rect.width, collision_mask_rect.height)

                if touching_collision_point[0] > 0:
                    #sprite.x += math.ceil(touching_collision_point[0]) * widest_point
                    collided_sprite.x -= math.ceil(touching_collision_point[0]) * widest_point
                else:
                    sprite.x += math.floor(touching_collision_point[0]) * widest_point
                    collided_sprite.x -= math.floor(touching_collision_point[0]) * widest_point
                
                if touching_collision_point[1] > 0:
                    #sprite.y -= math.ceil(touching_collision_point[1]) * widest_point
                    collided_sprite.y -= math.ceil(touching_collision_point[1]) * widest_point
                else:
                    #sprite.y += math.floor(touching_collision_point[1]) * widest_point
                    collided_sprite.y -= math.floor(touching_collision_point[1]) * widest_point

                collided_sprite.rect.centerx = collided_sprite.x
                collided_sprite.rect.centery = collided_sprite.y
                #sprite.rect.centerx = sprite.x
                #sprite.rect.centery = sprite.y

                # #update mask positions
                #image_center = sprite.image.get_rect(center = (sprite.x, sprite.y)).center
                #sprite.rect = sprite.image.get_rect(center = image_center)
                #sprite.mask = pygame.mask.from_surface(sprite.image, 240)
                #update mask positions
                image_center = collided_sprite.image.get_rect(center = (collided_sprite.x, collided_sprite.y)).center
                collided_sprite.rect = collided_sprite.image.get_rect(center = image_center)
                collided_sprite.mask = pygame.mask.from_surface(collided_sprite.image, 240)

                count *= 2
                touching_collision_mask_point = pygame.sprite.collide_mask(sprite, collided_sprite)
                if count > 100:
                    sprite.kill()
                touching = False#touching_collision_mask_point is not None

            pygame.draw.circle(sprite.image, (255, 0, 0), collision_mask_point, 10)

            #pygame.draw.circle(sprite.image, (0,255,0), sprite.mask.to_surface().get_bounding_rect().center, 5)
            
            collision_mask_rect = sprite.mask.to_surface().get_bounding_rect()
            #collision_mask_rect = sprite.image.get_bounding_rect()
            collision_point = Vector2(collision_mask_rect.center) - Vector2(collision_mask_point)

            #do projection of self velocity in collision point direction
            collision_point_normal = collision_point#collision_point.rotate(180)

            #finally, cancel out velocity change from update()
            sprite.x -= sprite.vector[0]
            sprite.y -= sprite.vector[1]
            sprite.rect.centerx = sprite.x
            sprite.rect.centery = sprite.y

            #use reflect to bounce vector off of rotated collision point
            if sprite.vector and sprite.vector.magnitude() != 0:
                pygame.math.Vector2.reflect_ip(sprite.vector, collision_point_normal)
                #sprite.vector += sprite.vector.reflect(collision_point_normal)
                #pygame.math.Vector2.rotate_ip(sprite.vector, 180)

            #collision_mask_point = pygame.sprite.collide_mask(sprite, collided_sprite)

    def on_collision(self, collision_list: List[Sprite]) -> None:
        for sprite in collision_list:
            if sprite == self:
                return
            PhysicsSprite.process_single_collision(sprite, self)
            PhysicsSprite.process_single_collision(self, sprite)

    
   
                


class SpaceShip(PhysicsSprite):
        def __init__(self, initialX, initialY, initialDx, initialDy):
            # Call the parent class (Sprite) constructor
            PhysicsSprite.__init__(self, initialX, initialY, initialDx, initialDy)
            tempImageRect = spriteSheet.getSpriteRect("ship")
            self.image = spriteSheet.image_at(tempImageRect)
            self.image = pygame.mask.from_surface(self.image, 240).to_surface(unsetcolor=(0,0,0,0))
            self.originalImage = self.image
            self.rect = Rect(initialX, initialY,
                                tempImageRect.width, tempImageRect.height)
            self.mask = pygame.mask.from_surface(self.image, 240)
            self.thrust_on = False
            self.THRUST_STRENGTH = 0.3 # pixels/frame
            self.ROTATION_STRENGTH = 4 # degrees
            self.INERTIAL_DAMPENING = 0.99 # float from 0-1
            self.radius = 10

        def draw_thrust(self):
            if self.thrust_on:
                tempImageRect = spriteSheet.getSpriteRect("shipThrust")
                self.image = spriteSheet.image_at(tempImageRect)
                self.image = pygame.mask.from_surface(self.image, 240).to_surface(unsetcolor=(0,0,0,0))
                self.originalImage = self.image
            else:
                tempImageRect = spriteSheet.getSpriteRect("ship")
                self.image = spriteSheet.image_at(tempImageRect)
                self.image = pygame.mask.from_surface(self.image, 240).to_surface(unsetcolor=(0,0,0,0))
                self.originalImage = self.image
        
        def update(self, *args, **kwargs) -> None:
            pressed = pygame.key.get_pressed()
            #a key, rotate counter-clockwise
            if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
                self.angle += self.ROTATION_STRENGTH
            #d key, rotate clockwise
            if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
                self.angle -= self.ROTATION_STRENGTH
            #w key, thrust
            if pressed[pygame.K_w] or pressed[pygame.K_UP]:
                self.thrust_on = True
                thrustVector = Vector2(
                    self.THRUST_STRENGTH * math.cos(-math.radians(self.angle)),
                    self.THRUST_STRENGTH * math.sin(-math.radians(self.angle))
                )
                self.vector += thrustVector
            else:
                self.thrust_on = False
                #inertial dampeners
                self.vector *= self.INERTIAL_DAMPENING

            self.draw_thrust()
            #self.angle += -1
            return super().update(*args, **kwargs)
    

class Asteroid(PhysicsSprite):
    def __init__(self, initialX, initialY, initialDx, initialDy, initialRot, size = 3):
        # Call the parent class (Sprite) constructor
        PhysicsSprite.__init__(self, initialX, initialY, initialDx, initialDy)
        
        key = ""
        #hack to get asteroids images
        if size == 3:
            key += "bigA"
        elif size == 2:
            key +="a"
        elif size == 1:
            key += "smA"
        else:
            pass
        if size > 0:
            key += "steroid"
            key += str(random.randint(1,3))

        tempImageRect = spriteSheet.getSpriteRect(key)
        self.image = spriteSheet.image_at(tempImageRect)
        self.image = pygame.mask.from_surface(self.image, 240).to_surface(unsetcolor=(0,0,0,0))
        self.originalImage = self.image
        self.rect = Rect(initialX, initialY,
                            tempImageRect.width, tempImageRect.height)
        self.mask = pygame.mask.from_surface(self.image, 240)
        self.size = size
        self.initalRot = initialRot
        self.radius = 80

    def update(self, *args, **kwargs) -> None:
        if self.size <= 0:
            self.kill()
        self.angle -= math.radians(self.initalRot)
        return super().update(*args, **kwargs)

    # def on_collision(self, collision_list: List[Sprite]) -> None:
    #     for sprite in collision_list:
    #         if sprite == self:
    #             return super().on_collision(collision_list)
    #         #find collision point
    #         collision_mask_point = pygame.sprite.collide_mask(sprite, self)
    #         if collision_mask_point is None:
    #             return super().on_collision(collision_list)

    #     self.size-= 1
    #     #get new image
    #     key = ""
    #     #hack to get asteroids images
    #     if self.size == 3:
    #         key += "bigA"
    #     elif self.size == 2:
    #         key +="a"
    #     elif self.size == 1:
    #         key += "smA"
    #     else:
    #         pass
    #     if self.size > 0:
    #         key += "steroid"
    #         key += str(random.randint(1,3))
    #         tempImageRect = spriteSheet.getSpriteRect(key)
    #         self.image = spriteSheet.image_at(tempImageRect)
    #         self.image = pygame.mask.from_surface(self.image, 240).to_surface(unsetcolor=(0,0,0,0))
    #         self.originalImage = self.image
    #         self.rect = Rect(self.x, self.y,
    #                             tempImageRect.width, tempImageRect.height)
    #         self.mask = pygame.mask.from_surface(self.image, 240)
    #     return super().on_collision(collision_list)

if __name__ == "__main__":
    pygame.init()
    size = (WIDTH, HEIGHT)
    window = pygame.display.set_mode(size)

    running = True
    clock = pygame.time.Clock()

    all_sprites = Group()

    spaceship = SpaceShip(WIDTH/2, HEIGHT/2, 0, 0)
    all_sprites.add(spaceship)

    for x in range(25):
        asteroid = Asteroid(
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            random.uniform(0.3, 1) * random.choice([-1, 1]),
            random.uniform(0.3, 1) * random.choice([-1, 1]),
            random.randint(5, 15) * random.choice([-1, 1]),
            random.randint(1, 3)
        )
        print(asteroid.x, asteroid.y, asteroid.vector.x, asteroid.vector.y, asteroid.initalRot)
        all_sprites.add(asteroid)

    while running:
        keyEvent = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update(*all_sprites)
        hit_list = pygame.sprite.groupcollide( all_sprites, all_sprites, False, False, pygame.sprite.collide_mask)
        for sprite in hit_list.keys():
            sprite.on_collision( hit_list[ sprite ] )

        # main drawing loop
        window.fill(BLACK)
        
        # Draw all sprites
        all_sprites.draw(window)
        pygame.display.flip()

        # render tick
        clock.tick(60)
    pygame.quit()
    sys.exit()
