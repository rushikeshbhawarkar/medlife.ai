# # Purpose: Small provider interface so the AI vendor can be swapped through configuration.
# # Add a provider implementation here only if the common interface needs to change.
# from abc import ABC, abstractmethod

# class AIProvider(ABC):
#     @abstractmethod
#     def answer(self, query: str) -> str:
#         raise NotImplementedError





# Purpose: Small provider interface so the AI vendor can be swapped through configuration.
from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def answer(self, query: str, context: str = "") -> str:
        raise NotImplementedError
