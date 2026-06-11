from dataclasses import Field
from experta import *

class ScoredNode(Fact):
    node_id = Field(str, mandatory=True)