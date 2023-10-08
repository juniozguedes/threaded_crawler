# Create venv

```
python -m venv venv
```

# Install requirements

Windows:

```
.\venv\Scripts\pip.exe install -r requirements.txt
```

Linux:

```
source venv/bin/activate
pip install -r requirements.txt
```

# Install playwright

Windows:

```
.\venv\Scripts\playwright install
```

Linux:

```
playwright install
```

# Run the project

```
flask run
```

# Where to check outputs:

```
company_csv module:
A CSV with the urls will be generated at scrappers > company_csv > companies_output.csv

Also the function will print the urls and the employee count as requested
```

```
g2crowd module:
A JSON with the review data will be generated at scrappers > g2crowd > g2crowd_output.json

Also the function will print significant steps/data about the scrapping
```
