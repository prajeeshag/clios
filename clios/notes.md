
# Notes

- `Annotated[dict, jsonReader]` can be used to type hint an argument of the operator function which expects a `dict` but in the cli it expects a <str> `filename` and `jsonReader(filename)` will return `dict`
- To extend this idea one can annotate `input` in the same way and the `output` as `Annotated[someType, someTypeWriter]`
- Generalizing this idea for `input` and `output` we can define `DataTransformers`. `DataTransformers` convert data from one type to another. `File` is just one of the type. Thus a `DataReader` class is just a subclass of the `DataTransformer` class which transform the `file` object to the desired datatype object.
- In fact DataTransformers are just callables with single input
- assert `output` type at runtime 

## Error Messages
- Error messages can be documented as rules if written affirmatively

## Type checking and Type hints
- If you are asking me something tell me the type (Ask for type hints)
- If you are saying you will return a particular type (Ask for type hints). And I will cross-check your promise at runtime
- If I am telling that I will give something I will make sure that I keep the promise (Don't ask for type hints)



## Misc
- Variadic argument can be at the starting or at the end. Depending upon where it is placed the argument parsing will change.
- In case Variadic keyword argument any 'key' is a valid key as long as the type is correct
- Input: 
    - tuple[int] equivalent to int
    - tuple[int,...] and list[int] are both variadic inputs of same type int will be provided as tuple in the first case and list in the second

## Testing
- While mocking an implemented object, mock the correct behaviour
- While mocking an yet to implement object, document the expected behaviour 