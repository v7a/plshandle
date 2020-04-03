# plshandle
Create a contract between caller and function that requires the caller to handle specific
exceptions raised by the function.

## Why?
Sometimes, we just _have to_ recover from an error. And because you are a human being, you might not
always keep exception handling in mind at all times. This library helps reduce this mental overhead.
