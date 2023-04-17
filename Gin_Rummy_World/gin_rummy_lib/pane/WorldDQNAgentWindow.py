import panel as pn
import torch

from rlcard.games.gin_rummy.game import GinRummyGame
from rlcard.agents import DQNAgent

from DQNAgentPane import DQNAgentPane
from World import World
from util import to_int_list

class WorldDQNAgentWindow(pn.Column):

    def __init__(self, world: World):
        super().__init__()
        self.world = world
        window_title = pn.pane.Markdown("# World DQNAgent Window")
        dqn_agent_settings_title = pn.pane.Markdown("## DQN Agent Settings")
        self.controls = WorldDQNAgentControls(world=world)

        title = pn.pane.Markdown("### DQN Agent Settings")
        self.dqn_agent_pane = DQNAgentPane(dqn_agent=world.agent)
        self.dqn_agent_view = pn.Column(title, self.dqn_agent_pane)
        self.dqn_agent_view.width_policy = 'max'
        self.dqn_agent_view.height_policy = 'max'

        content = pn.Row(self.controls, self.dqn_agent_view)
        self.append(window_title)
        self.append(content)
        self.width_policy = 'max'
        self.background = 'green'

        ### hook up value controls
        for control in self.controls.value_controls:
            control.param.watch(self.update, 'value')

        ### hook up create_dqn_agent_button
        self.controls.create_dqn_agent_button.on_click(self.create_dqn_agent)

    def create_dqn_agent(self, event):
        agent = None
        #device = get_device() # Check whether gpu is available
        agent_path = self.world.agent_path
        if os.path.exists(agent_path):
            pass
        else:
            exception_error = None
            try: # Note this: kludge
                state_shape = to_int_list(self.state_shape)
            except Exception as error:
                exception_error = error
            try: # Note this: kludge
                mlp_layers = to_int_list(self.mlp_layers)
            except Exception as error:
                exception_error = error
            if not exception_error:
                game = GinRummyGame() # Note this
                num_actions = game.get_num_actions()
                agent = DQNAgent(
                    replay_memory_size=self.replay_memory_size,
                    replay_memory_init_size=self.replay_memory_init_size,
                    update_target_estimator_every=self.update_target_estimator_every,
                    discount_factor=self.discount_factor,
                    epsilon_start=self.epsilon_start,
                    epsilon_end=self.epsilon_end,
                    epsilon_decay_steps=self.epsilon_decay_steps,
                    batch_size=self.batch_size,
                    num_actions=num_actions, # Note this: kludge
                    state_shape=state_shape, # Note this: kludge
                    train_every=self.train_every,
                    mlp_layers=mlp_layers, # Note this: kludge
                    #device=device,
                    learning_rate=self.learning_rate)
                torch.save(agent, agent_path)
                self.batch_size = 60
                #print(f'train_steps={agent.train_t} time_steps={agent.total_t}')
                #print(agent.q_estimator.qnet)
        # FIXME: show fail/success message
    
    def update(self, event):
        agent = self.world.agent
        agent.memory.memory_size = self.controls.replay_memory_size_input.value
        agent.replay_memory_init_size = self.controls.replay_memory_init_size_input.value
        agent.update_target_estimator_every = self.controls.update_target_estimator_every_input.value
        agent.discount_factor = self.controls.discount_factor_input.value
        agent.epsilons[0] = self.controls.epsilon_start_input.value
        agent.epsilons[-1] = self.controls.epsilon_end_input.value
        agent.epsilon_decay_steps = self.controls.epsilon_decay_steps_input.value
        agent.batch_size = self.controls.batch_size_input.value
        agent.train_every = self.controls.train_every_input.value
        agent.q_estimator.learning_rate = self.controls.learning_rate_input.value
        agent.q_estimator.num_actions = self.controls.num_actions_input.value
        try:
            agent.q_estimator.state_shape = to_int_list(self.controls.state_shape_input.value)
        except:
            pass
        try:
            agent.q_estimator.mlp_layers = to_int_list(self.controls.mlp_layers_input.value)
        except:
            pass
        self.world.dqn_agent_config.model_name = self.controls.model_name_input.value

        self.dqn_agent_pane.object = self.dqn_agent_pane.get_markdown(dqn_agent=self.world.agent)

class WorldDQNAgentControls(pn.Row):

    def __init__(self, world: World):
        super().__init__()

        # max values
        max_replay_memory_size = 20000
        max_replay_memory_init_size = 10000
        max_update_target_estimator_every = 10000
        max_discount_factor = 1.00
        max_epsilon_start = 1.0
        max_epsilon_end = 0.5 # 0.1
        max_epsilon_decay_steps = 20000
        max_batch_size = 128
        max_train_every = 10
        max_learning_rate = 1.0

        max_num_actions = 1000

        # current values
        dqn_agent = world.agent
        replay_memory_size = min(dqn_agent.memory.memory_size, max_replay_memory_size)
        replay_memory_init_size = min(dqn_agent.replay_memory_init_size, max_replay_memory_init_size)
        update_target_estimator_every = min(dqn_agent.update_target_estimator_every, max_update_target_estimator_every)
        discount_factor = min(dqn_agent.discount_factor, max_discount_factor)
        epsilon_start = min(dqn_agent.epsilons[0], max_epsilon_start)
        epsilon_end = min(dqn_agent.epsilons[-1], max_epsilon_end)
        epsilon_decay_steps = min(dqn_agent.epsilon_decay_steps, max_epsilon_decay_steps)
        batch_size = min(dqn_agent.batch_size, max_batch_size)
        train_every = min(dqn_agent.train_every, max_train_every)
        learning_rate = min(dqn_agent.q_estimator.learning_rate, max_learning_rate)
        state_shape = str(dqn_agent.q_estimator.state_shape)
        mlp_layers = str(dqn_agent.q_estimator.mlp_layers)
        model_name = world.dqn_agent_config.model_name

        num_actions = min(world.get_game_num_actions(), max_num_actions)

        # begin init
        self.margin_x = 10
        self.margin_y = 4

        self.value_controls = []
        self.columns = [pn.Column(), pn.Column(), pn.Column()]

        self.column_index = 0
        self.replay_memory_size_input = self.make_int_input(name='replay_memory_size', value=replay_memory_size, start=1000, end=max_replay_memory_size, step=1000)
        self.replay_memory_init_size_input = self.make_int_input(name='replay_memory_init_size', value=replay_memory_init_size, start=1000, end=max_replay_memory_init_size, step=1000)
        self.update_target_estimator_every_input = self.make_int_input(name='update_target_estimator_every', value=update_target_estimator_every, start=1000, end=max_update_target_estimator_every, step=1000)
        self.discount_factor_input = self.make_float_input(name='discount_factor', value=discount_factor, end=max_discount_factor)
        self.epsilon_start_input = self.make_float_input(name='epsilon_start', value=epsilon_start, end=max_epsilon_start)
        self.epsilon_end_input = self.make_float_input(name='epsilon_end', value=epsilon_end, end=max_epsilon_end)
        self.epsilon_decay_steps_input = self.make_float_input(name='epsilon_decay_steps', value=epsilon_decay_steps, end=max_epsilon_decay_steps)
        self.batch_size_input = self.make_int_input(name='batch_size', value=batch_size, end=max_batch_size)
        self.train_every_input = self.make_int_input(name='train_every', value=train_every, end=max_train_every)
        self.learning_rate_input = self.make_float_input(name='learning_rate', value=learning_rate, end=max_learning_rate)

        self.column_index = 1
        self.num_actions_input = self.make_int_input(name='num_actions', value=num_actions, start=1, end=max_num_actions)
        self.state_shape_input = self.make_text_input(name='state_shape', value=state_shape)
        self.mlp_layers_input = self.make_text_input(name='mlp_layers', value=mlp_layers) # [128, 128, 128]  # [128, 128, 128] # [64, 64, 64] # [64, 64]

        self.column_index = 2
        self.model_name_input = self.make_text_input(name='model_name', value=model_name)
        self.create_dqn_agent_button = self.make_button(name='Create DQN agent')

        self.append(self.columns[0])
        self.append(self.columns[1])
        self.append(self.columns[2])
    
    def make_int_input(self, name, value=0, start=0, end=10, step=1):
        result = pn.widgets.IntInput(name=name, value=value, start=start, end=end, step=step)
        result.width_policy = 'min'
        result.min_width = 100
        result.margin = [self.margin_y, self.margin_x, self.margin_y, self.margin_x]
        self.columns[self.column_index].append(result)
        self.value_controls.append(result)
        return result
    
    def make_float_input(self, name, value=0, start=0, end=1, step=0.01):
        result = pn.widgets.FloatInput(name=name, value=value, start=start, end=end, step=step)
        result.width_policy = 'min'
        result.min_width = 100
        result.margin = [self.margin_y, self.margin_x, self.margin_y, self.margin_x]
        self.columns[self.column_index].append(result)
        self.value_controls.append(result)
        return result
    
    def make_text_input(self, name: str, value: str = ''):
        result = pn.widgets.TextInput(name=name, value=value)
        self.columns[self.column_index].append(result)
        self.value_controls.append(result)
        return result
    
    def make_button(self, name: str):
        result = pn.widgets.Button(name=name)
        result.width_policy = 'min'
        self.columns[self.column_index].append(result)
        return result