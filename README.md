[![CircleCI](https://circleci.com/gh/duckietown/duckietown-serialization.svg?style=shield)](https://circleci.com/gh/duckietown/duckietown-serialization)


# Duckietown Serialization Library

This package implements a simple and extensible serialization protocol
with backend JSON or YAML.


## Goals

- both JSON and YAML backend. 
- built with forward-compatibility in mind
- data can be interpreted/read even without having the class definition
- good for configuration files editing

## Simple example


Some examples:

```yaml

~Point:
    x: 0
    y: 1

```

```python
    
class Point(Serializable):
  def __init__(self, x, y):
      self.x = x
      self.y = y

```

Now you can load:

```python


s="""
~Point:
    x: 0
    y: 1
"""

from duckietown_serialization_ds1 import Serializable
import yaml
data = yaml.load(s)
p = Serializable.from_json_dict(data)
assert isinstance(p, Point)

```


## Wire format

An "object" is represented by a dictionary with fields of the type "`~ClassName`".

For example:

```yaml
my-object:
    ~ClassName:
        attribute1: 1
        attribute2: 2
```

This represents an object of class `ClassName` with two attributes.

If the class has multiple bases, there are different entries for each class:


```yaml
my-object:
    ~BaseClass:
        attribute0: 0
    ~DerivedClass:
        attribute1: 1
        attribute2: 2
```

This opens up a good way to have forward compatibility: 
if an implementation doesn't know `DerivedClass` it can just interpret
the portion of `BaseClass`.



## Metadata



```yaml
~:
  ds-version: [ds1]
  dependencies:
    ~Dependencies:
      ClassName: python_module>=1.3
      
~ClassName:
   
    
```
