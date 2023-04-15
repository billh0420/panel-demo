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
        self.append(('Trainer', TrainerPane(world=self.world)))
        self.append(('GameSettings', GameSettingsPane(world=self.world)))
        self.dynamic = True
        self.height = 800