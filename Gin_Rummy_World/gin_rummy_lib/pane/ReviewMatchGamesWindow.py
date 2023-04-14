import panel as pn

from World import World
from ReviewPlayWindow import ReviewPlayWindow
from DQNAgentPane import DQNAgentPane
from TrainerPane import TrainerPane
from GameSettingsPane import GameSettingsPane

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