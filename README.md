# Flask Document Generator
Flask Doc Gen is a simple flask extension which allows you to generate Open API Documentation for your flask applications by just increasing your code testing coverage 

## Installation
Install Flask Document Generator with pip by running the below command:
```
pip3 install git+https://github.com/bhargavcn/flask_doc_gen.git
```

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

Initalize the document generator instance with the flask app
```python
doc_gen.init_app(app)
```
