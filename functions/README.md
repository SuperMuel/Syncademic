Firebase Cloud Functions cannot use `poetry` to manage dependencies. Instead, it uses `requirements.txt` to manage dependencies. Thus, we need to convert the `pyproject.toml` file to `requirements.txt`.

1. Install Poetry "Export" plugin
```bash
poetry self add poetry-export
```

2. Inside the `functions` directory, run : 
```bash
poetry export --without-hashes -f requirements.txt -o requirements.txt
```

