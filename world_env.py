from stable_baselines3 import PPO
import gym
import pygame
import numpy as np
import random
import sys
from gym import spaces
from functions import Wall, lineRectIntersectionPoints

class TurretEnv(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['human']}
  difficulty = 20
  # Window size
  frame_size_x = 600
  frame_size_y = 600

  # Colors (R, G, B)
  black = pygame.Color(0, 0, 0)
  red = pygame.Color(255, 0, 0)
  green = pygame.Color(0, 255, 0)

  # Action Constants
  LEFT = 0
  RIGHT = 1
  UP = 2
  DOWN = 3
  #STAY = 4  # add later the STAY action for the agent to not move.
  


  def __init__(self):
     super(TurretEnv, self).__init__()
     pygame.init()
	# Initialise game window
     pygame.display.set_caption('Hide from Turret')
	# FPS (frames per second) controller
     self.fps_controller = pygame.time.Clock()
     self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y))
	# Game variable and functions

     rnd_pos = [random.randrange(1, (self.frame_size_x // 50)) * 50,
                       random.randrange(1, (self.frame_size_y // 50)) * 50] # Random spawning of agent.

     self.agent_pos = rnd_pos        # agent position
     self.prev_agent_pos = rnd_pos   # agent previous position
     self.seen = False               # agent visible
     self.Hp = 20                    # Health Point of the agent. If HP == 0, game end.
     self.game_over = False
     self.turret_pos = [300, 300]    # Turret position
     self.direction = 'RIGHT'
     self.change_to = self.direction # change direction of agent
     self.counter = 0                # counter 


     number_of_actions = 4          # number of actions possible in env, if we add STAY the number should be 5
     number_of_observations = 5     # parameter observed, position of agent,position of turret, HP

     self.action_space = spaces.Discrete(number_of_actions)
     self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(number_of_observations,), dtype=np.float32)
	


  def step(self, action):  # Step in the env, repeated every frame
      
      self.counter += 1
      if self.counter > 50:
          return np.array([self.agent_pos[0], self.agent_pos[1], self.turret_pos[0], self.turret_pos[1],self.Hp], dtype=np.float32), -100, True, {}
      if self.seen == True:
        self.Hp -= 2             # The agent is visible, losing HP
      if self.Hp <= 0:
         reward = -50            # - 50 reward and game_over 
         self.game_over = True
       
      # Movement of the agent 
      if action == self.UP:
          self.change_to = 'UP'
      if action == self.DOWN:
          self.change_to = 'DOWN'
      if action == self.LEFT:
          self.change_to = 'LEFT'
      if action == self.RIGHT:
          self.change_to = 'RIGHT'
    #   if action == self.STAY:
    #       self.change_to = 'STAY'    # New action to be assigned later, the agent can stay in the same place

      # For the agent to not move in the opposite direction instantaneously
      if self.change_to == 'UP' and self.direction != 'DOWN':
          self.direction = 'UP'
      if self.change_to == 'DOWN' and self.direction != 'UP':
          self.direction = 'DOWN'
      if self.change_to == 'LEFT' and self.direction != 'RIGHT':
          self.direction = 'LEFT'
      if self.change_to == 'RIGHT' and self.direction != 'LEFT':
          self.direction = 'RIGHT'
     
     # Moving the agent
      if self.direction == 'UP':
          self.agent_pos[1] -= 50
      if self.direction == 'DOWN':
          self.agent_pos[1] += 50
      if self.direction == 'LEFT':
          self.agent_pos[0] -= 50
      if self.direction == 'RIGHT':
          self.agent_pos[0] += 50
      #if self.direction == 'STAY':
      #    self.agent_pos[0]=self.agent_pos[0]  # Failed solution need something else
      #   self.agent_pos[1]=self.agent_pos[1]

      # Limit the agent in the window
      if self.agent_pos[0] < 0:
        self.agent_pos[0] += 50
      elif self.agent_pos[0] > self.frame_size_x - 50:
          self.agent_pos[0] -= 50
      if self.agent_pos[1] < 0:
        self.agent_pos[1] += 50
      elif self.agent_pos[1] > self.frame_size_y - 50:
          self.agent_pos[1] -= 50
	
     # Define walls 

      global wall_sprites # later for wall collisions (not included yet)
      wall_sprites = pygame.sprite.Group()
      central_block = Wall( 100, 50, 50, 50 )  
      first_block = Wall(100,100,150,150)
      sec_block = Wall(150,350,50,50)
      thi_block = Wall(100,400,150,100)
      fo_block = Wall(100,100,150,150)
      fi_block = Wall(200,500,50,50)	
      si_block = Wall(400,50,50,200)
      se_block = Wall(450,100,100,100)
      ei_block = Wall(400,400,100,150)
      ni_block = Wall(500,400,50,50)
      wall_sprites.add(first_block)
      wall_sprites.add(sec_block),wall_sprites.add(thi_block),wall_sprites.add(fo_block),wall_sprites.add(fi_block),	  
      wall_sprites.add(central_block),wall_sprites.add(si_block),wall_sprites.add(se_block),wall_sprites.add(ei_block)
      wall_sprites.add(ni_block)
      
	  # Wall collisions test (Failed: not good enough)
    #   for wall in wall_sprites:
    #     if pygame.Rect.colliderect(wall.getRect(),player):
    #       if self.direction == 'UP':
    #        self.agent_pos[1] += 50
    #       if self.direction == 'DOWN':
    #        self.agent_pos[1] -= 50
    #       if self.direction == 'LEFT':
    #         self.agent_pos[0] += 50
    #       if self.direction == 'RIGHT':
    #         self.agent_pos[0] -= 50

      # Turret Sight
      # Does the line agent to turret intersect any obstacles?
      line_of_sight = [ self.agent_pos[0], self.agent_pos[1], self.turret_pos[0], self.turret_pos[1]]
      self.seen = True
      for wall in wall_sprites:
            # is anyting blocking the line-of-sight?
            intersection_points = lineRectIntersectionPoints( line_of_sight, wall.getRect() , game_window = self.game_window)
            if ( len( intersection_points ) > 0 ):
                self.seen = False # agent not visible to turret
                break


     # Reward rules

      reward = 0
      if self.seen == False:
         reward = 10 + self.Hp
      elif self.seen == True:
         reward = -2
      elif abs(self.agent_pos[0] - self.turret_pos[0]) + abs(self.agent_pos[1] - self.turret_pos[1]) > abs(self.prev_agent_pos[0] - self.turret_pos[0]) + abs(self.prev_agent_pos[1] - self.turret_pos[1]):
         reward = 1 # reward for staying away from turret
      elif abs(self.agent_pos[0] - self.turret_pos[0]) + abs(self.agent_pos[1] - self.turret_pos[1]) < abs(self.prev_agent_pos[0] - self.turret_pos[0]) + abs(self.prev_agent_pos[1] - self.turret_pos[1]):
         reward = -1 # - reward for getting closer to turret

      self.prev_agent_pos = self.agent_pos.copy()
      done = self.game_over
      info = {}
      #print(reward)
      return np.array([self.agent_pos[0], self.agent_pos[1], self.turret_pos[0], self.turret_pos[1],self.Hp], dtype=np.float32), reward, done, info

  def reset(self): # initial variables every step
     rnd_pos = [random.randrange(1, (self.frame_size_x // 50)) * 50,
                       random.randrange(1, (self.frame_size_y // 50)) * 50]
     self.agent_pos = rnd_pos
     self.prev_agent_pos = rnd_pos
     self.seen = False
     self.Hp = 20
     self.game_over = False
     self.turret_pos = [300, 300]
     self.direction = 'RIGHT'
     self.change_to = self.direction
     self.counter = 0
     return np.array([self.agent_pos[0], self.agent_pos[1], self.turret_pos[0], self.turret_pos[1],self.Hp], dtype=np.float32)

  def render(self, mode='human'):  # render of the ENV
      # GFX
      self.game_window.fill(self.black) # background Black
      pygame.event.get()                # help for the event in the env, solution for Window not responding
      # Define walls positions to be draw
      wall_sprites = pygame.sprite.Group()
      central_block = Wall( 100, 50, 50, 50 )  
      first_block = Wall(100,100,150,150)
      sec_block = Wall(150,350,50,50)
      thi_block = Wall(100,400,150,100)
      fo_block = Wall(100,100,150,150)
      fi_block = Wall(200,500,50,50)	
      si_block = Wall(400,50,50,200)
      se_block = Wall(450,100,100,100)
      ei_block = Wall(400,400,100,150)
      ni_block = Wall(500,400,50,50)
      wall_sprites.add(first_block)
      wall_sprites.add(sec_block),wall_sprites.add(thi_block),wall_sprites.add(fo_block),wall_sprites.add(fi_block),	  
      wall_sprites.add(central_block),wall_sprites.add(si_block),wall_sprites.add(se_block),wall_sprites.add(ei_block)
      wall_sprites.add(ni_block)
      
      # Draw line between the Turret and Agent, when agent is visible the line become white.
      if self.seen == True :
            pygame.draw.line( self.game_window, ( 200, 200, 200), self.agent_pos, self.turret_pos )
      else:
             pygame.draw.line( self.game_window, ( 50, 50, 50), self.agent_pos, self.turret_pos )

      # Draw Turret
      pygame.draw.rect(self.game_window, self.red, pygame.Rect(self.turret_pos[0], self.turret_pos[1], 50, 50))
      wall_sprites.draw(self.game_window)
      # Draw Agent
      pygame.draw.rect(self.game_window, self.green, pygame.Rect(self.agent_pos[0], self.agent_pos[1], 50, 50))
      # Refresh game screen
      pygame.display.update()
      # Refresh rate
      self.fps_controller.tick(self.difficulty)

  def close (self):
      pygame.quit()
      sys.exit()


########################################## Test with PPO model ######################################
# env = TurretEnv()
# model = PPO('MlpPolicy', env, verbose=1)
# model.learn(total_timesteps=200000)
# model.save("Turret_ai_model")
# # model = PPO.load("Turret_ai_model")
# obs = env.reset()
# for i in range(10000):
#     action, _state = model.predict(obs, deterministic=True)
#     obs, reward, done, info = env.step(action)
#     env.render()
#     if done:
#       obs = env.reset()
  




    

	    
