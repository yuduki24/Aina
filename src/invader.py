import pygame
from pygame.locals import *
import os
import sys
import random
import loader

START, PLAY, GAMEOVER, GAMECLEAR = (0, 1, 2, 3)  # ゲーム状態
SCR_RECT = Rect(0, 0, 640, 480)

class Invader:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption(u"Invader 07 ゲームオーバー画面")
        # 素材のロード
        self.load_images()
        self.load_sounds()
        # ゲームオブジェクトを初期化
        self.init_game()
        # メインループ開始
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()
    def init_game(self):
        """ゲームオブジェクトを初期化"""
        # ゲーム状態
        self.game_state = START
        # スプライトグループを作成して登録
        self.all = pygame.sprite.RenderUpdates()
        self.aliens = pygame.sprite.Group()  # エイリアングループ
        self.shots = pygame.sprite.Group()   # ミサイルグループ
        self.beams = pygame.sprite.Group()   # ビームグループ
        # デフォルトスプライトグループを登録
        Player.containers = self.all
        Shot.containers = self.all, self.shots
        Alien.containers = self.all, self.aliens
        Beam.containers = self.all, self.beams
        Explosion.containers = self.all
        # 自機を作成
        self.player = Player()
        # エイリアンを作成
        for i in range(0, 50):
            x = 20 + int(i % 10) * 40
            y = 20 + int(i / 10) * 40
            Alien((x,y))
    def update(self):
        """ゲーム状態の更新"""
        if self.game_state == PLAY:
            self.all.update()
            # ミサイルとエイリアンの衝突判定
            self.collision_detection()
            # エイリアンをすべて倒したらゲームオーバー
            if len(self.aliens.sprites()) == 0:
                self.game_state = GAMEOVER
    def draw(self, screen):
        """描画"""
        screen.fill((0, 0, 0))
        if self.game_state == START:  # スタート画面
            # タイトルを描画
            title_font = pygame.font.SysFont(None, 80)
            title = title_font.render("INVADER GAME", False, (255,0,0))
            screen.blit(title, ((SCR_RECT.width-title.get_width())/2, 100))
            # エイリアンを描画
            alien_image = Alien.images[0]
            screen.blit(alien_image, ((SCR_RECT.width-alien_image.get_width())/2, 200))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (255,255,255))
            screen.blit(push_space, ((SCR_RECT.width-push_space.get_width())/2, 300))
            # クレジットを描画
            credit_font = pygame.font.SysFont(None, 20)
            credit = credit_font.render(u"2008 http://pygame.skr.jp", False, (255,255,255))
            screen.blit(credit, ((SCR_RECT.width-credit.get_width())/2, 380))
        elif self.game_state == PLAY:  # ゲームプレイ画面
            self.all.draw(screen)
        elif self.game_state == GAMEOVER:  # ゲームオーバー画面
            # GAME OVERを描画
            gameover_font = pygame.font.SysFont(None, 80)
            gameover = gameover_font.render("GAME OVER", False, (255,0,0))
            screen.blit(gameover, ((SCR_RECT.width-gameover.get_width())/2, 100))
            # エイリアンを描画
            alien_image = Alien.images[0]
            screen.blit(alien_image, ((SCR_RECT.width-alien_image.get_width())/2, 200))
            # PUSH STARTを描画
            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (255,255,255))
            screen.blit(push_space, ((SCR_RECT.width-push_space.get_width())/2, 300))
    def key_handler(self):
        """キーハンドラー"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.game_state == START:  # スタート画面でスペースを押したとき
                    self.game_state = PLAY
                elif self.game_state == GAMEOVER:  # ゲームオーバー画面でスペースを押したとき
                    self.init_game()  # ゲームを初期化して再開
                    self.game_state = PLAY
    def collision_detection(self):
        """衝突判定"""
        # エイリアンとミサイルの衝突判定
        alien_collided = pygame.sprite.groupcollide(self.aliens, self.shots, True,  True)
        # # 貫通弾（Alienは消滅するがShotは消滅しない）
        # alien_collided = pygame.sprite.groupcollide(self.aliens, self.shots, True, False)
        # # 無敵のエイリアン（エイリアンは消滅しないがShotは消滅する
        # alien_collided = pygame.sprite.groupcollide(self.aliens, self.shots, False, True)
        for alien in alien_collided.keys():
            Alien.kill_sound.play()
            Explosion(alien.rect.center)  # エイリアンの中心で爆発
            # プレイヤーとビームの衝突判定
        beam_collided = pygame.sprite.spritecollide(self.player, self.beams, True)
        if beam_collided:  # プレイヤーと衝突したビームがあれば
            Player.bomb_sound.play()
            self.game_state = GAMEOVER  # ゲームオーバー！
    def load_images(self):
        """イメージのロード"""
        # スプライトの画像を登録
        Player.image = loader.load_image("player.png")
        Shot.image = loader.load_image("shot.png")
        Beam.image = loader.load_image("beam.png")
        # 画像を分割してロード
        Alien.images = loader.split_image(loader.load_image("alien.png"), 2)
        Explosion.images = loader.split_image(loader.load_image("explosion.png"), 16)
    def load_sounds(self):
        """サウンドのロード"""
        Player.shot_sound = loader.load_sound("shot.wav")
        Alien.kill_sound = loader.load_sound("kill.wav")
        Player.bomb_sound = loader.load_sound("bomb.wav")

def collision_detection(player, shots, aliens, beams):
    """衝突判定"""
    # エイリアンとミサイルの衝突判定
    alien_collided = pygame.sprite.groupcollide(aliens, shots, True, True)
    # # 貫通弾（Alienは消滅するがShotは消滅しない）
    # alien_collided = pygame.sprite.groupcollide(aliens, shots, True, False)
    # # 無敵のエイリアン（エイリアンは消滅しないがShotは消滅する
    # alien_collided = pygame.sprite.groupcollide(aliens, shots, False, True)
    for alien in alien_collided.keys():
        Alien.kill_sound.play()
        Explosion(alien.rect.center)  # エイリアンの中心で爆発
    # プレイヤーとビームの衝突判定
    beam_collided = pygame.sprite.spritecollide(player, beams, True)
    if beam_collided:  # プレイヤーと衝突したビームがあれば
        Player.bomb_sound.play()
        # TODO: ゲームオーバー処理

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
    prob_beam = 0.005  # ビームを発射する確率
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
        # ビームを発射
        if random.random() < self.prob_beam:
            Beam(self.rect.center)
        # キャラクターアニメーション
        self.frame += 1
        self.image = self.images[int(self.frame/self.animcycle%2)]

class Beam(pygame.sprite.Sprite):
    """エイリアンが発射するビーム"""
    speed = 5  # 移動速度
    def __init__(self, pos):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def update(self):
        self.rect.move_ip(0, self.speed)  # 下へ移動
        if self.rect.bottom > SCR_RECT.height:  # 下端に達したら除去
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """爆発エフェクト"""
    animcycle = 2  # アニメーション速度
    frame = 0
    def __init__(self, pos):
        # imagesとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.max_frame = len(self.images) * self.animcycle  # 消滅するフレーム
    def update(self):
        # キャラクターアニメーション
        self.image = self.images[int(self.frame/self.animcycle)]
        self.frame += 1
        if self.frame == self.max_frame:
            self.kill()  # 消滅

if __name__ == "__main__":
    Invader()
