from uuid import UUID

stub_data_assets = [
    {
        "file": "",
        "id": UUID("ccebc2e9-d710-4943-8bae-947fa1492d7f"),
        "name": "Graph With CSV Import",
        "type": "value",
        "date": "1372944000",
        "text": 5,
        "code": {
            "text": "import pandas as pd\ndf = pd.read_csv('simple_data.csv')\ns = df['a'].sum()",
            "tokens": [
                {
                    "line": 2,
                    "start": 1,
                    "end": 3,
                    "intermediate": {
                        "file": "",
                        "id": UUID("e01d7a89-0d6d-474b-8119-b5f087cbd66e"),
                        "name": "",
                        "type": "dataset",
                        "date": "1272944000",
                    },
                }
            ],
        },
    },
    {
        "file": "boston_house_prices.csv",
        "id": UUID("3e68e66a-e743-4e0e-bd64-d2fdf7ee5c71"),
        "name": "Boston House Prices",
        "type": "dataset",
        "date": "1372944000",
        "code": {
            "text": 'print("Hello World")',
            "tokens": [
                {
                    "line": 1,
                    "start": 1,
                    "end": 6,
                    "intermediate": {
                        "file": "chart2.png",
                        "id": 10,
                        "name": "Value vs Year",
                        "type": "chart",
                        "date": "1272944000",
                    },
                },
            ],
        },
        "rest_endpoint": "https://acme.linea.ai/models?modelName=housing_model&data_point=[your_data]",
        "refresh_config": {
            "auto_refresh": True,
            "refresh_on_data_update": False,
            "refresh_on_frequency": True,
            "frequency": "Every Sunday",
            "notification": [],
        },
    },
    {
        "file": "chart1.png",
        "id": UUID("47d48b5e-2c73-44d7-9940-ba7b882d0892"),
        "name": "Area vs Value",
        "type": "chart",
        "date": "1172944000",
        "code": {
            "text": "def generate_chart(data):\n\treturn data\nchart = generate_chart(data)",
            "tokens": [
                {
                    "line": 3,
                    "start": 1,
                    "end": 6,
                    "intermediate": {
                        "file": "chart2.png",
                        "id": 10,
                        "name": "Value vs Year",
                        "type": "chart",
                        "date": "1272944000",
                    },
                },
                {
                    "line": 1,
                    "start": 1,
                    "end": 4,
                    "intermediate": {
                        "file": "boston_house_prices.csv",
                        "id": 6,
                        "name": "Boston House Prices",
                        "type": "dataset",
                        "date": "1372944000",
                    },
                },
            ],
        },
        "rest_endpoint": "https://acme.linea.ai/models?modelName=housing_model&data_point=[your_data]",
        "refresh_config": {
            "auto_refresh": True,
            "refresh_on_data_update": False,
            "refresh_on_frequency": True,
            "frequency": "Every Sunday",
            "notification": [],
        },
    },
    {
        "file": "chart2.png",
        "id": UUID("fc4c174b-adaa-49b5-892c-b4886efaa5b8"),
        "name": "Value vs Year",
        "type": "chart",
        "date": "1272944000",
        "rest_endpoint": "https://acme.linea.ai/models?modelName=housing_model&data_point=[your_data]",
        "refresh_config": {
            "auto_refresh": True,
            "refresh_on_data_update": False,
            "refresh_on_frequency": True,
            "frequency": "Every Sunday",
            "notification": [],
        },
    },
    {
        "file": "beemovie.txt",
        "id": UUID("97285057-c672-48d9-9266-ef0ee876479d"),
        "name": "Bee Movie",
        "type": "array",
        "date": "1072944000",
        "rest_endpoint": "https://acme.linea.ai/models?modelName=housing_model&data_point=[your_data]",
        "refresh_config": {
            "auto_refresh": True,
            "refresh_on_data_update": False,
            "refresh_on_frequency": True,
            "frequency": "Every Sunday",
            "notification": [],
        },
    },
    {
        "file": "birds.txt",
        "id": UUID("b11c4955-c284-4e67-be10-fda488feaf23"),
        "name": "Birds",
        "type": "array",
        "date": "1572944000",
        "rest_endpoint": "https://acme.linea.ai/models?modelName=housing_model&data_point=[your_data]",
        "refresh_config": {
            "auto_refresh": True,
            "refresh_on_data_update": False,
            "refresh_on_frequency": True,
            "frequency": "Every Sunday",
            "notification": [],
        },
    },
]
