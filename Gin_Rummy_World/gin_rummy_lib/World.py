import os
import torch
import pandas as pd
import panel as pn

from rlcard.utils import get_device
from rlcard.agents import DQNAgent

from rlcard.games.gin_rummy.game import GinRummyGame
from rlcard.games.gin_rummy.utils.settings import Setting, Settings
from rlcard.models.gin_rummy_rule_models import GinRummyNoviceRuleAgent

from util import get_current_time
from DQNAgentConfig import DQNAgentConfig
from RLTrainerConfig import RLTrainerConfig
from RLTrainer import RLTrainer
from GinRummyRookie01RuleAgent import GinRummyRookie01RuleAgent
from GinRummyScorer230402 import GinRummyScorer230402
from GameReviewer import GameReviewer

class World:

    def __init__(self, world_dir:str or None = None):
        self.world_dir = world_dir if world_dir else os.path.abspath('.')
        # Game settings
        if not os.path.exists(self.game_settings_path):
            default_game_settings = Setting.default_setting()
            default_game_settings_dict = dict((k.value, v) for (k, v) in default_game_settings.items())
            game_settings_df = pd.DataFrame([default_game_settings_dict])
            game_settings_df.to_json(self.game_settings_path)
        self.game_settings = pd.read_json(self.game_settings_path)

        # GameScorer
        self.game_scorer = GinRummyScorer230402()

        # Define configs
        self.dqn_agent_config = DQNAgentConfig()
        self.rl_trainer_config = RLTrainerConfig()

        # More stuff
        self.agent = self.create_dqn_agent()
        self.opponent_agent = GinRummyNoviceRuleAgent()

        # GameReviewer
        self.max_review_episodes = 100
        self.view_width = 1200
        self.gameReviewer = None
        self.play_review_match(max_review_episodes=0)

        # opponents
        self.opponents = []
        self.opponents.append(GinRummyNoviceRuleAgent())

    def save_game_settings(self):
        self.game_settings.to_json(self.game_settings_path)

    @property
    def game_settings_path(self):
        return os.path.join(self.world_dir, f'game_settings.json')
    
    @property
    def agent_dir(self):
        config = self.dqn_agent_config
        return f'{self.world_dir}/{config.model_name}'
    
    @property
    def agent_path(self):
        config = self.dqn_agent_config
        return f'{self.agent_dir}/{config.model_name}.pth'
    
    @property
    def game_settings_dict(self):
        result = dict()
        world_game_settings_dicts = self.game_settings.to_dict(orient='records')
        if len(world_game_settings_dicts) == 1:
            result = world_game_settings_dicts[0]
        return result
    
    def get_game_num_actions(self) -> int:
        game = self.make_game()
        num_actions = game.get_num_actions()
        return num_actions

    def make_game(self) -> GinRummyGame:
        game = GinRummyGame()
        settings = Settings()
        settings.change_settings(self.game_settings_dict)
        game.settings = settings
        game.judge.scorer = self.game_scorer
        return game
 
    def play_train_match(self, num_episodes: int or None = None):
        if self.agent:
            game = self.make_game()
            opponent = GinRummyRookie01RuleAgent()
            opponents = [opponent]
            dqn_agent_config = self.dqn_agent_config
            rl_trainer_config = self.rl_trainer_config
            # Print current configuration
            print("Starting training")
            game.settings.print_settings()
            print(f"Start: {get_current_time()}")
            print(self.dqn_agent_config)
            print(self.rl_trainer_config)
            print(f'train_steps={self.agent.train_t} time_steps={self.agent.total_t}')
            print('----- agent.q_estimator.qnet -----')
            print(self.agent.q_estimator.qnet)
            # train agent
            actual_num_episodes = num_episodes if num_episodes else self.rl_trainer_config.num_episodes
            rlTrainer = RLTrainer(
                game=game,
                agent=self.agent,
                opponents=opponents,
                log_dir=self.agent_dir,
                dqn_agent_config=dqn_agent_config,
                rl_trainer_config=rl_trainer_config)
            rlTrainer.train(num_episodes=actual_num_episodes)
        else:
            print("You need to create a dqn_agent")
            
    def play_review_match(self, max_review_episodes: int):
        game = self.make_game()
        agents = [self.agent, self.opponent_agent]
        if not self.gameReviewer:
            self.gameReviewer = GameReviewer(game=game, agents=agents, view_width=self.view_width)
        self.gameReviewer.play_review_match(game=game, agents=agents, max_review_episodes=max_review_episodes, view_width=self.view_width)

    def create_dqn_agent(self):
        agent = None
        config = self.dqn_agent_config
        device = get_device() # Check whether gpu is available
        if os.path.exists(self.agent_path):
            agent = torch.load(self.agent_path, map_location=device)
            agent.set_device(device)
        elif os.path.exists(self.game_settings_path):
            game = self.make_game()
            num_actions = game.get_num_actions()
            state_shape = config.state_shape # state_shape for player_id = 0
            agent = DQNAgent(
                replay_memory_size=config.replay_memory_size,
                replay_memory_init_size=config.replay_memory_init_size,
                update_target_estimator_every=config.update_target_estimator_every,
                discount_factor=config.discount_factor,
                epsilon_start=config.epsilon_start,
                epsilon_end=config.epsilon_end,
                epsilon_decay_steps=config.epsilon_decay_steps,
                batch_size=config.batch_size,
                num_actions=num_actions,
                state_shape=state_shape,
                train_every=config.train_every,
                mlp_layers=config.mlp_layers,
                learning_rate=config.learning_rate,
                device=device)
        return agent