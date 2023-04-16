import panel as pn

from World import World

class DQNAgentPane(pn.pane.Markdown):

    def __init__(self, world: World):
        super().__init__()
        agent = world.agent
        markdown = f"""
            <div class="special_table"></div>
            | Name | Value |
            | :--: | :--: |
            | replay_memory_size | {agent.memory.memory_size} |
            | replay_memory_init_size | {agent.replay_memory_init_size} |
            | update_target_estimator_every | {agent.update_target_estimator_every} |
            | discount_factor | {agent.discount_factor} |
            | epsilon_start | {agent.epsilons[0]} |
            | epsilon_end | {agent.epsilons[-1]} |
            | epsilon_decay_steps | {agent.epsilon_decay_steps} |
            | batch_size | {agent.batch_size} |
            | train_every | {agent.train_every} |
            | learning_rate | {agent.q_estimator.learning_rate} |
            | num_actions | {agent.num_actions} |
            | state_shape | {agent.q_estimator.state_shape} |
            | mlp_layers | {agent.q_estimator.mlp_layers} |
        """
        self.width_policy = 'max'
        self.object = markdown