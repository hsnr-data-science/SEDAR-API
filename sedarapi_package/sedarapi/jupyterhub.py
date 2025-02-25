# Import needed python modules
from __future__ import annotations
from typing import Type

# Import needed SEDAR modules
from .commons import Commons

##################################################
##                                              ##
##          This class is not used yet          ##
##                                              ##
##################################################

#--------------------------------------------------------------
class Jupyterhub:
    def __init__(self, connection: Type[Commons]):
        self.connection = connection
        self.jupyter_base_url = "http://127.0.0.1:8000/hub/login"


        # For a later implementation it could be considered to create an interface to jupyterhub itself.
        