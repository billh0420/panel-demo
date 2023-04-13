import os
import torch
import pandas as pd
import rlcard
from rlcard.utils import Logger, plot_curve, tournament, reorganize

from util import get_player_rows

import DQNAgentConfig
import RLTrainerConfig

class RLTrainer:

    def __init__(self, game, agent, opponents, log_dir: str,
                    dqn_agent_config: DQNAgentConfig,
                    rl_trainer_config: RLTrainerConfig):
        self.game = game
        self.agents = [agent] + opponents
        self.algorithm:str = rl_trainer_config.algorithm
        self.num_episodes:int = rl_trainer_config.num_episodes
        self.num_eval_games:int = rl_trainer_config.num_eval_games
        self.log_dir = log_dir
        self.model_name:str = dqn_agent_config.model_name
        self.evaluate_every = max(1, min(self.num_episodes // 20, 10000))

    def train(self, num_episodes:int):
        evaluate_every = max(1, min(num_episodes // 20, 10000))
        print(f'actual num_episodes={num_episodes}')
        print(f'actual evaluate_every={evaluate_every}')
        env = rlcard.make('gin-rummy', config={'seed': None})
        env.game = self.game
        env.set_agents(self.agents)

        all_rows = []

        # Start training
        with Logger(self.log_dir) as logger:
            for episode in range(num_episodes):

                if self.algorithm == 'nfsp':
                    self.agents[0].sample_episode_policy()

                # Generate data from the environment
                trajectories, payoffs = env.run(is_training=True)

                # wch: extra       
                rows = get_player_rows(player_id=0, trajectories=trajectories)
                all_rows.extend(rows)

                # Reorganaize the data to be state, action, reward, next_state, done
                trajectories = reorganize(trajectories, payoffs)

                # Feed transitions into agent memory, and train the agent
                # Here, we assume that DQN always plays the first position
                # and the other players play randomly (if any)
                for ts in trajectories[0]:
                    self.agents[0].feed(ts)

                # Evaluate the performance. Play with random agents.
                if episode % evaluate_every == 0:
                    logger.log_performance(
                        episode,
                        tournament(
                            env,
                            self.num_eval_games,
                        )[0]
                    )

            # Get the paths
            csv_path, fig_path = logger.csv_path, logger.fig_path

        # Plot the learning curve
        plot_curve(csv_path, fig_path, self.algorithm)

        # Save model
        save_path = os.path.join(self.log_dir, f'{self.model_name}.pth')
        torch.save(self.agents[0], save_path)
        print('Model saved in', save_path)

        # Save all_rows
        df_save_path = os.path.join(self.log_dir, 'all_rows.json')
        columns = ['held_cards_num', 'top_card_num', 'dead_cards_num', 'opponent_known_cards_num', 'unknown_cards_num', 'legal_actions', 'action']
        df = pd.DataFrame(all_rows, columns = columns)
        df.to_json(df_save_path)