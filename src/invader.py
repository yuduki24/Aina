import pygame
from pygame.locals import *
import os
import sys
import loader

SCR_RECT = Rect(0, 0, 640, 480)

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)
    pygame.display.set_caption(u"Invader")
    
    # スプライトグループを作成して登録
    all = pygame.sprite.RenderUpdates()
    aliens = pygame.sprite.Group()  # エイリアングループ
    shots = pygame.sprite.Group()   # ミサイルグループ
    Player.containers = all
    Shot.containers = all, shots
    Alien.containers = all, aliens
    # スプライトの画像を登録
    Player.image = loader.load_image("player.png")
    Shot.image = loader.load_image("shot.png")
    # エイリアンの画像を分割してロード
    Alien.images = loader.split_image(loader.load_image("alien.png"))

    # 効果音のロード.
    Player.shot_sound = loader.load_sound("shot.wav")
    Alien.kill_sound = loader.load_sound("kill.wav")
    # 自機を作成
    Player()
    # エイリアンを作成
    for i in range(0, 50):
        x = 20 + int(i % 10) * 40
        y = 20 + int(i / 10) * 40
        Alien((x,y)) 

    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        screen.fill((0, 0, 0))
        all.update()
        all.draw(screen)
        pygame.display.update()
        collision_detection(shots, aliens)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

def collision_detection(shots, aliens):
    """衝突判定"""
    # エイリアンとミサイルの衝突判定
    alien_collided = pygame.sprite.groupcollide(aliens, shots, True, True)
    # # 貫通弾（Alienは消滅するがShotは消滅しない）
    # alien_collided = pygame.sprite.groupcollide(aliens, shots, True, False)
    # # 無敵のエイリアン（エイリアンは消滅しないがShotは消滅する
    # alien_collided = pygame.sprite.groupcollide(aliens, shots, False, True)
    for alien in alien_collided.keys():
        Alien.kill_sound.play()

class Player(pygame.sprite.Sprite):
    """自機"""
    speed = 5  # 移動速度
    reload_time = 15  # リロード時間
    def __init__(self):
        # imageとcontainersはmain()でセットされる
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom  # プレイヤーが画面の一番下
        self.reload_timer = 0
    def update(self):
        # 押されているキーをチェック
        pressed_keys = pygame.key.get_pressed()
        # 押されているキーに応じてプレイヤーを移動
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        elif pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        self.rect.clamp_ip(SCR_RECT)
        # ミサイルの発射
        if pressed_keys[K_SPACE]:
            # リロード時間が0になるまで再発射できない
            if self.reload_timer > 0:
                # リロード中
                self.reload_timer -= 1
            else:
                # 発射！！！
                Player.shot_sound.play()
                Shot(self.rect.center)  # 作成すると同時にallに追加される
                self.reload_timer = self.reload_time

class Shot(pygame.sprite.Sprite):
    """プレイヤーが発射するミサイル"""
    speed = 9  # 移動速度
    def __init__(self, pos):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos  # 中心座標をposに
    def update(self):
        self.rect.move_ip(0, -self.speed)  # 上へ移動
        if self.rect.top < 0:  # 上端に達したら除去
            self.kill()

class Alien(pygame.sprite.Sprite):
    """エイリアン"""
    speed = 2  # 移動速度
    animcycle = 18  # アニメーション速度
    frame = 0
    move_width = 230  # 横方向の移動範囲
    def __init__(self, pos):
        # imagesとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.left = pos[0]  # 移動できる左端
        self.right = self.left + self.move_width  # 移動できる右端
    def update(self):
        # 横方向への移動
        self.rect.move_ip(self.speed, 0)
        if self.rect.center[0] < self.left or self.rect.center[0] > self.right:
            self.speed = -self.speed
        # キャラクターアニメーション
        self.frame += 1
        self.image = self.images[int(self.frame/self.animcycle%2)]

if __name__ == "__main__":
    main()
