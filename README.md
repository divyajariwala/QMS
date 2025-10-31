# product-complaint-ai-usecase
This repository contains the code for a product complaint analysis AI use case. The application is designed to analyze customer complaints about products and provide insights using natural language processing techniques.

# To run tests on local environment

- Install the dependencies
```bash
pip install -r src/test/requirements.txt
```

- Export the PYTHONPATH
```bash
export PYTHONPATH=$(pwd)/src/app
```

- Run the test
```bash
pytest src/tests \                                                                                                                                                                                                                                                                                                  ─╯
  --cov=src/app \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=70 -W ignore
```
