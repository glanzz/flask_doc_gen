# Flask Document Generator
Generate Open API Documentation for your flask applications by just increasing your code testing coverage 

## Getting Started
Initialize a document generator instance
```python
doc_gen = DocGen(
    title="My Flask App",
    version="1.0.0",
    description="APIs of My Flask App",
    servers=[
        {
            "url": "https://flaskapp.com/api/v1",
            "description": "Production URL of the application",
        },
        {
            "url": "https://flaskapp.dev/api/v1",
            "description": "Dev Environment",
        },
    ],
)

```

## Installation
Install Flask Document Generator with pip by running the below command:
```
pip3 install git+https://github.com/bhargavcn/flask_doc_gen.git
```
