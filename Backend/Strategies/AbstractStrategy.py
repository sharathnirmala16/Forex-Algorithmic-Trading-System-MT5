import pandas as pd
from abc import ABC, abstractmethod

class Strategy(ABC):
    
    #attributes
    _strategy_id = ''
    _modified_df = pd.DataFrame()

    #Constructor
    def __init__(self, strategy_id : str) -> None:
        self._strategy_id = strategy_id

    #getters and setters
    @property
    def strategy_id(self) -> str:
        return self._strategy_id
    
    @property
    def modified_df(self) -> pd.DataFrame:
        return self._modified_df
