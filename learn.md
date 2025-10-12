yeild
context manager: A context manager is any object that implements two special methods:

__enter__(self)
__exit__(self, exc_type, exc_val, exc_tb)

| Concept       | Explanation                                                            |
| ------------- | ---------------------------------------------------------------------- |
| What it is    | Object that manages setup and teardown automatically                   |
| Syntax        | `with <context_manager> as <var>:`                                     |
| Magic methods | `__enter__` and `__exit__`                                             |
| Purpose       | Ensures cleanup (file close, release lock, etc.) even if errors happen |


when you do : 
with something as value:
Python actually does this:

value = something.__enter__()
try:
    # your block
finally:
    something.__exit__(exc_type, exc_val, exc_tb)


from contextlib import contextmanager

@contextmanager
def my_context():
    print("Setup")
    yield "Resource"
    print("Cleanup")

with my_context() as res:
    print("Using", res)


Setup
Using Resource
Cleanup

###############################################

from abc import ABC, abstractmethod

class BaseDataSource(ABC):
    @abstractmethod
    def fetch_candidates(self, job_id: str):
        pass

    @abstractmethod
    def fetch_job_metadata(self, job_id: str):
        pass


An abstract class is a class that cannot be instantiated directly, and is meant to be a blueprint for other classes.

An abstract method is a method that must be implemented by any subclass of the abstract class.


###############################################

walrus operator : 

chunk = list(islice(it, size))
if chunk:
    yield chunk
    
With the walrus operator, you can combine these into one line:

if chunk := list(islice(it, size)):
    yield chunk
    
###############################################

islice: 

islice comes from Python’s itertools module.
It means "iterator slice" — it lets you slice an iterator without turning the whole thing into a list.

Import it like this:

from itertools import islice



