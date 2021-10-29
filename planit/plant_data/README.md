# Model

Data management with `sqlite3`.

Provided functions are

- `overwrite(name: str)`
- `add_plant(common_name: str) -> bool`,
- `add_symbiosis_score(plant_a: str, plant_b: str, score: int) -> bool`,
- `get_all_plants() -> List[str]` and
- `get_symbiosis_score(plant_a: str, plant_b: str) -> int`.

## Usage

The provided functions can be used by importing this module via `from planit import model` and `model.<function-name>`.

## Example

```python
# Imports
from planit import model
from typing import Dict

# Overwrite table plants
overwrite('plants')

# Add plants a and b
plant_data.add_plant('a')
plant_data.add_plant('b')

# Add symbiosis score
plant_data.add_symbiosis_score('a', 'b', 1)

# Get all plants
all_plants: Dict[str, str] = plant_data.get_all_plants()

# Get the symbiosis score of plant a and b
symbiosis_score_a_b: int = plant_data.get_symbiosis_score('a', 'b')
```
