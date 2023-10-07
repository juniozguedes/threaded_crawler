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

# Install Pre-commit (Optional)

```
pre-commit install
```

# Run the project

```
flask run
```

# Linter checking

To check pre-commit status:

```
 pre-commit run --all-files
```
