import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")
game_over = False
game_outcome = 0
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None

map_image = pg.image.load('image/tb_grass1.png').convert_alpha()

turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'tw/tw{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)

cursor_turret = pg.image.load('image/tower1.png').convert_alpha()

enemy_images = {
    "weak": pg.image.load('enemy/enemy_1.png').convert_alpha(),
    "medium": pg.image.load('enemy/enemy_2.png').convert_alpha(),
    "strong": pg.image.load('enemy/enemy_3.png').convert_alpha(),
    "elite": pg.image.load('enemy/enemy_4.png').convert_alpha()
}

buy_turret_image = pg.image.load('image/button2.png').convert_alpha()
cancel_image = pg.image.load('image/button1.png').convert_alpha()
upgrade_turret_image = pg.image.load('image/up.png').convert_alpha()
begin_image = pg.image.load('image/begin.png').convert_alpha()
restart_image = pg.image.load('image/begin.png').convert_alpha()

map_image = pg.transform.scale(map_image, (c.map_width, c.map_height))

with open('levels/level.tmj') as file:
    world_data = json.load(file)
text_font = pg.font.SysFont("Consolas", 24, bold=True)
large_font = pg.font.SysFont("Consolas", 36)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x

    if world.tile_map[mouse_tile_num] == 7:
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False

        if space_is_free == True:
            new_turret = Turret(turret_spritesheets,
                                mouse_tile_x, mouse_tile_y)
            turret_group.add(new_turret)
            # deduct cost of turret
            world.money -= c.BUY_COST


def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret


def clear_selection():
    for turret in turret_group:
        turret.selected = False


world = World(world_data, map_image)
world.process_data()
world.process_enemies()
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)

run = True
while run:
    clock.tick(c.FPS)
    if game_over == False:
        if world.health <= 0:
            game_over = True
            game_outcome = -1  # loss

        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1  # win

        enemy_group.update(world)
        turret_group.update(enemy_group)

        if selected_turret:
            selected_turret.selected = True

    screen.fill("grey100")
    world.draw(screen)
    enemy_group.draw(screen)

    for turret in turret_group:
        turret.draw(screen)
    draw_text(str(world.health), text_font, "grey100", 0, 0)
    draw_text(str(world.money), text_font, "grey100", 0, 30)
    draw_text(str(world.level), text_font, "grey100", 0, 60)

    if game_over == False:
        if level_started == False:
            if begin_button.draw(screen):
                level_started = True

        else:
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        if world.check_level_complete() == True:
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()

        if turret_button.draw(screen):
            placing_turrets = True

        if placing_turrets == True:
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos

            if cursor_pos[0] <= c.SCREEN_WIDTH:
                screen.blit(cursor_turret, cursor_rect)

            if cancel_button.draw(screen):
                placing_turrets = False

        if selected_turret:
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST

    else:
        pg.draw.rect(screen, "dodgerblue",
                     (200, 200, 400, 200), border_radius=30)

        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)

        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)

        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            enemy_group.empty()
            turret_group.empty()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                selected_turret = None
                clear_selection()

                if placing_turrets == True:
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)

                else:
                    selected_turret = select_turret(mouse_pos)

    pg.display.flip()
pg.quit()