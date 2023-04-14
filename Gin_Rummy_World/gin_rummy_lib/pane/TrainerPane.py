import panel as pn

from World import World

class TrainerPane(pn.pane.Markdown):

    def __init__(self, world: World):
        super().__init__()
        rl_trainer_config = world.rl_trainer_config
        dqn_agent_config = world.dqn_agent_config # FIXME
        markdown = f"""
        # Trainer
        algorithm: {rl_trainer_config.algorithm}

        num_episodes: {rl_trainer_config.num_episodes}

        num_eval_games: {rl_trainer_config.num_eval_games}

        evaluate_every: {rl_trainer_config.evaluate_every}

        log_dir: {world.agent_dir}
        """
        self.width = world.view_width
        self.object = markdown