# tests/conftest.py
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from streetracer.registration      import RegistrationModule
from streetracer.crewManagement    import CrewManagementModule
from streetracer.inventory         import InventoryModule
from streetracer.raceManagement    import RaceManagementModule
from streetracer.results           import ResultsModule
from streetracer.missionPlanning   import MissionPlanningModule
from streetracer.reputationRivalry import ReputationRivalryModule
from streetracer.garargeWorkshop    import GarageWorkshopModule

@pytest.fixture
def reg():
    return RegistrationModule()

@pytest.fixture
def crew(reg):
    return CrewManagementModule(reg)

@pytest.fixture
def inv(request):
    starting_cash = getattr(request, "param", 10_000)
    return InventoryModule(starting_cash)

@pytest.fixture
def race(crew, inv):
    return RaceManagementModule(crew, inv)

@pytest.fixture
def res(race, crew, inv):
    return ResultsModule(race, crew, inv)

@pytest.fixture
def mis(crew, inv):
    return MissionPlanningModule(crew, inv)

@pytest.fixture
def rep():
    return ReputationRivalryModule()

@pytest.fixture
def ws(inv, crew):
    return GarageWorkshopModule(inv, crew)