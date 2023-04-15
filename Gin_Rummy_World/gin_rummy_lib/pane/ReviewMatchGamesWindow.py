import panel as pn

from World import World
from pane.ReviewPlayWindow import ReviewPlayWindow
from pane.DQNAgentPane import DQNAgentPane
from pane.TrainerPane import TrainerPane
from pane.GameSettingsPane import GameSettingsPane

class ReviewMatchGamesWindow(pn.Tabs):

    def __init__(self, world: World):
        super().__init__()
        self.world = world
        self.append(('Review', ReviewPlayWindow(world=self.world)))
        self.append(('DQNAgent', DQNAgentPane(world=self.world)))
        self.append(('Trainer', self.trainer_view))
        self.append(('GameSettings', GameSettingsPane(world=self.world)))
        self.dynamic = True
        self.height = 800

    @property
    def trainer_view(self):
        trainer_title = pn.pane.Markdown("# RL Trainer Settings")
        trainer_pane = TrainerPane(world=self.world)
        trainer_view = pn.Column(trainer_title, trainer_pane, sizing_mode = 'stretch_width')
        return trainer_view