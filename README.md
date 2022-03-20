**1) Clone the repository** 

    git clone https://github.com/rchr1/tum-ects.git
    cd tum-ects
    
**2) Create and run the containers**

    docker-compose up

The api will be available at `localhost:5000`. The parser needs a few hours to collect all degrees.

**Exemplary calls:**

Status:

    http://107.173.251.156:5000
    
    {
        "crawled_degrees": 8
    }

Degree:

    http://107.173.251.156:5000/degree?degree_id=17_722&list_modules=0

    {
        "pStpStpNr": 290,
        "info": {
        "degree_id": "17 722",
        "title": {
            "german": "[20061] Bachelorstudiengang Agrarwissenschaften und Gartenbauwissenschaften",
            "english": "[20061] Agricultural Science and Horticultural Science"
        },
            "subtitle": {
                "german": "17 722 Agrarwissenschaften und Gartenbauwissenschaften (20061, Bachelorstudium, auslaufend)",
                "english": "17 722 Agricultural Science and Horticultural Science (20061, Bachelor's program, discontinued)"
            }
        }
    }

Module:

    http://107.173.251.156:5000/module?degree_id=17_722&module_id=WZ7374
    
    {
        "module_id": "WZ7374",
        "title": {
            "german": "[WZ7374] Biologie 3 + 4",
            "english": "[WZ7374] Biology 3 + 4"
        },
        "ects": 5.0,
        "weighting_factor": 1.0
    }
 
Degrees which contain a given module:

    http://107.173.251.156:5000/parents?module_id=WZ2755

    {
        "degree_ids": [
            "11 800"
        ]
    }

