# framable
Crafting your Python into frames 


## The point 
We aim to illustrate usual programming concept via DataFrames.
This can be both useful and interesting, as we now can visually (especially in notebooks)
have a confirmation of our mental representation for these concepts, with more than code.


## The guide
Spivak's book "Category Theory for the Sciences" details how to see data tables from a categorical viewpoint.
This should help us to find how to represent programming(ie. categorical) concepts as dataframes.


## Status
We need to keep using these in different contexts, and keep experimenting, in order to refine the best dataframe representation for these:

- dataclass (like a table of instance records)
- procedure (like a trace)

If you find any issue with these usecases, please report an issue !

## TODO: Protocol
In the spirit for PEP544, we should define a Framable protocol, that will help us extract a frame from python classes. 


## Roadmap
We need to work to find a good enough dataframe representation for these:

- class-instance method
- coroutine
- generator
- async generator
- base python class


If you have any idea for these usecases, please make a pull request !
