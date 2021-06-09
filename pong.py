import numpy as np
import pygame

class pong_game:
    def __init__(self,player_mode = "bot",display=True):
        self.display = display

        self.player_mode = player_mode #"bot" or "player"
        self.score_bot = 0
        self.score_player = 0
        self.score = (self.score_bot,self.score_player)

        self.h = int(256)
        self.w = int(512)
        self.ball_size = 4
        self.paddle_thickness = 4
        
        self.keys = [False,False]
        self.paddle_length = int(28*1.5)

        self.paddle_speed = 7
        self.vX_init = -6
        self.vY_init = np.random.randint(-4,4)

        self.vX = self.vX_init
        self.vY = self.vY_init
        
        self.rand_list = [0,0,1]
        self.rand_list_lock = [0,0,0,0,1]

        self.posL_paddle = int((self.h-self.paddle_length)/2)
        self.l_coords = self.get_l_paddle_coords(self.posL_paddle)
        
        self.posR_paddle = int((self.h-self.paddle_length)/2)
        self.r_coords = self.get_r_paddle_coords(self.posR_paddle)

        self.posR = int(self.h/2)
        self.posC = int(self.w/2)
        
        self.ball_coords = self.get_ball_coords(self.posR,self.posC)
        
        if self.display:
            pygame.init()
            self.disp = pygame.display.set_mode(size=(self.w,self.h))
            self.paddle = pygame.surfarray.make_surface(self.draw_paddle())
            self.ball = pygame.surfarray.make_surface(self.draw_ball())
            pygame.display.set_caption(str(self.score_bot)+"          pong         "+str(self.score_player))
        self.run()

    def run(self):
        while True:
            if self.display:
                self.pressed = pygame.key.get_pressed()
                self.disp.fill((0,0,0))
                self.disp.blit(self.paddle,(4,self.posL_paddle))
                self.disp.blit(self.paddle,(self.w-6,self.posR_paddle))
                self.disp.blit(self.ball,(self.posC,self.posR))

                pygame.display.flip()
            
                for event in pygame.event.get():
                    #print(self.keys)
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.keys[0] = True
                        if event.key == pygame.K_DOWN:
                            self.keys[1] = True
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_UP:
                            self.keys[0] = False
                        if event.key == pygame.K_DOWN:
                            self.keys[1] = False

                pygame.time.wait(50)

            self.simulate_step()
            #print(self.score)
            if self.score_bot >= 6:
                print("bot wins")
                break
            elif self.score_player >= 6:
                print("player wins")
                break
        
        print(self.score)
        if self.display:
            pygame.quit()

    def simulate_step(self):
        self.posL_paddle = max(min(int(self.posL_paddle + self.get_paddle_next("l")),self.h-self.paddle_length),0)
        self.l_coords = self.get_l_paddle_coords(self.posL_paddle)

        self.posR_paddle = max(min(int(self.posR_paddle + self.get_paddle_next("r")),self.h-self.paddle_length),0)
        self.r_coords = self.get_r_paddle_coords(self.posR_paddle)

        self.posC = max(min(self.posC + self.vX,self.w),0)
        self.posR = max(min(self.posR + self.vY,self.h),0)
        self.ball_coords = self.get_ball_coords(self.posR,self.posC)
        
        self.check_r_paddle_collision()
        self.check_l_paddle_collision()
        self.check_top_collision()
        self.check_bot_collision()
        
        if self.posC > self.w-4:
            self.score_bot += 1
            self.score = (self.score_bot,self.score_player)
            #print(self.score)
            if self.display:
                pygame.display.set_caption(str(self.score_bot)+"          pong         "+str(self.score_player))
            self.reset_ball()
        elif self.posC < 4:
            self.score_player += 1
            self.score = (self.score_bot,self.score_player)
            #print(self.score)
            if self.display:
                pygame.display.set_caption(str(self.score_bot)+"          pong         "+str(self.score_player))
            self.reset_ball()
        #self.score = (self.score_bot,self.score_player)
       
    def get_paddle_next(self,side):
        #maps -1 to 1
        if side == "l":
            pos = self.get_l_update()
        elif side == "r":
            if self.player_mode == "player":
                pos = self.get_r_update()
            elif self.player_mode == "bot":
                pos = self.get_r_update_bot()
            else:
                raise Exception
        return int(pos)

    def get_l_update(self):
        mid = self.posL_paddle + self.paddle_length/2
        if self.posR > mid + self.paddle_length/8:
            return self.paddle_speed
        elif self.posR < mid - self.paddle_length/8:
            return -self.paddle_speed
        else:
            return 0

    def get_r_update(self):
        
        if self.keys[0]:
            return -self.paddle_speed
        elif self.keys[1]:
            return self.paddle_speed
        return 0
    
    def get_r_update_bot(self):
        mid = self.posR_paddle + self.paddle_length/2
        if self.posR > mid + self.paddle_length/8:
            return self.paddle_speed
        elif self.posR < mid - self.paddle_length/8:
            return -self.paddle_speed
        else:
            return 0

    def check_top_collision(self):
        if self.posR-2 <= 0:
            self.vY = -self.vY

    def check_bot_collision(self):
        if self.posR+2 >= self.h:
            self.vY = -self.vY

    def check_r_paddle_collision(self):
        collisions = set(self.ball_coords).intersection(self.r_coords)
        if bool(collisions):
            self.vY = self.get_new_vY("r")
            self.vX = -(self.vX + self.rand_list[np.random.randint(0,len(self.rand_list))]) #moving left
        
    def check_l_paddle_collision(self):
        collisions = set(self.ball_coords).intersection(self.l_coords)
        if bool(collisions):
            self.vY = self.get_new_vY("l")
            self.vX = -self.vX + self.rand_list[np.random.randint(0,len(self.rand_list))] #moving right

    def get_new_vY(self,side):
        if side == "r":
            paddle = int(self.posR_paddle + self.paddle_length/2)
        elif side == "l":
            paddle = int(self.posL_paddle + self.paddle_length/2)

        rel_pos = int(self.posR - paddle)
        vel_frac = rel_pos / (self.paddle_length/2)
        return int(10 * vel_frac) + self.rand_list_lock[np.random.randint(0,len(self.rand_list_lock))]

    def draw_paddle(self):
        return 255*np.ones((self.paddle_thickness,self.paddle_length))

    def draw_ball(self):
        return 255*np.ones((self.ball_size,self.ball_size))


    def reset_ball(self):
        self.posR = int(self.h/2)
        self.posC = int(self.w/2)
        
        self.ball_coords = self.get_ball_coords(self.posR,self.posC)

        self.vX = self.vX_init
        #self.vY = self.vY_init
        
        #self.vX = int((self.vX/abs(self.vX))*self.vX_init)
        self.vY = np.random.randint(-4,4)
   
    def get_l_paddle_coords(self,pos):
        coords = []
        for i in range(pos,pos+self.paddle_length):
            for j in range(4,6):
                coords.append((i,j))
        return coords
    
    def get_r_paddle_coords(self,pos):
        coords = []
        for i in range(pos,pos+self.paddle_length):
            for j in range(self.w-6,self.w-4):
                coords.append((i,j))
        return coords

    def get_ball_coords(self,posR,posC):
        coords = []
        for j in range(posC+2-abs(self.vX),posC+4+abs(self.vX)):
            coords.append((posR-2,j))
        for j in range(posC+1-abs(self.vX),posC+5+abs(self.vX)):
            coords.append((posR-1,j))
        for j in range(posC-abs(self.vX),posC+6+abs(self.vX)):
            coords.append((posR,j))
        for j in range(posC+1-abs(self.vX),posC+5+abs(self.vX)):
            coords.append((posR+1,j))
        for j in range(posC+2-abs(self.vX),posC+4+abs(self.vX)):
            coords.append((posR+2,j))
        return coords


if __name__ == "__main__":
    g = pong_game("player",True)
