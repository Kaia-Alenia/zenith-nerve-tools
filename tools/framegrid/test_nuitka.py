import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../libs')))
from alenia_bridge.integration import init_zenith
init_zenith(__file__)
