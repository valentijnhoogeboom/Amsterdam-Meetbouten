This script creates a spreadsheet containing all data of all 'meetbouten' in a street.
It uses the Amsterdam Data API (https://api.data.amsterdam.nl/v1/docs/index.html) to fetch the data per street. The data will be saved as output.csv

**Prerequisites**
- Install Python 3.12. This can either be done through the Microsoft Store App or using the link: https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-US&gl=US
- Restart your PC after installation of Python.
- Download this script using the Code button and unzip it.
- Run the ``setup`` script.

**Usage**
- Run the ``main`` file.
- Enter a street name.
- After execution a file named: ``output.csv`` should appear.

**Pitfalls**
- The street name might be case sensitive.
- You can't have the output.csv open while loading new street data.
