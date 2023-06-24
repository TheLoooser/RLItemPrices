# Rocket League Inventory Item Prices  
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Type checker: mypy](https://img.shields.io/badge/%20type_checker-mypy-%231674b1?style=flat)](https://mypy-lang.org/)
***

## Getting Started
### Prerequisites
- [Python 3](https://www.python.org/downloads/)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases)
- [Rocket League](https://www.rocketleague.com/)
- [Bakkesmod](https://bakkesplugins.com/)

### Installation

Windows (using PowerShell)

1. Create a virtual environment  
`python -m venv venv`
2. Install [GNU make](https://www.gnu.org/software/make/) on Windows with [chocolatey](https://chocolatey.org/install)  
`choco install make`
3. Activate the virtual environment  
`venv\Scripts\activate`
4. Set the proper user execution policy  
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted`

### Execution

1. Get your Rocket League item inventory data  
    - Start Bakkesmod
    - Start Rocket League
    - Dump inventory to CSV file: `F2 → Misc → Dump inventory to csv`
    - Copy the newly created file from `C:\Users\<Username>\AppData\Roaming\bakkesmod\bakkesmod\data\inventory.csv` to
   the root folder of this project.
2. Run the Makefile: `make all`
3. Run the Script: `python main.py`

#### Notes
- `make lint` will return with the following error `make: *** [Makefile:8: lint] Error 4` if the warnings are not disabled.  
This happens if the code is not rated 10/10, since `make` assumes that the command has failed because the invoked shell
return an exit code of 4 instead of 0, which would indicate success.
- The blueprint price option does not work, because the blueprint inventory dump is missing the item name, which is required
to match the item to its price. Unfortunately, the [Better Inventory Export](https://bakkesplugins.com/plugins/view/155) plugin of Bakkesmod also does 
not work as the item name of the blueprint is also not present there.

