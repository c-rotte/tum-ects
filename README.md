**1) Clone the repository** 

    git clone https://github.com/rchr1/tum-ects.git
    cd tum-ects
    
**2) Create and run the containers**

    docker-compose up -d

The api will be available at `localhost:5000`. The parser needs a few hours to collect all degrees.

***

**Notes:**

Every degree potentially has multiple versions and thus curricula / module details. The Bachelor's Informatics Program, for example, has multiple versions which all have the `degree_id` 17_030. These versions can be uniquely identified using their `pStpStpNr`. Thus, the `pStpStpNr` is used as the primary identifier for all api calls. 

The `language` can either be `german` or `english`. The default is `english`.

***

**Exemplary calls:**

(**Warning**: Do not use `107.173.251.156` in your application, it is just a low-end server)

Status:

    http://107.173.251.156:5000
    
    {
        "crawled_degrees": {
            "german": 1,
            "english": 1
        }
    }

All degree versions:

    http://107.173.251.156:5000/pStpStpNrs&language=english

    {
        "pStpStpNrs": [
            292
        ]
    }

Specific degree version:

    http://107.173.251.156:5000/degree?pStpStpNr=292&language=english

    {
        "degree_id": "16 751",
        "title": "[20081] Forestry and Wood Science",
        "subtitle": "16 751 Forestry and Wood Science (20081, Master's program, discontinued)",
        "curriculum_id": "20081",
        "pStpStpNr": 292
    }

Curriculum of a degree version:

    http://107.173.251.156:5000/curriculum?pStpStpNr=292?language=english
    
    {
        "curriculum": {
            "[20081] Forestry and Wood Science": {
                "Required Modules": {
                    "WZ4004": {
                        "module_id": "WZ4004",
                        "ects": 5.0,
                        "weighting_factor": 1.0,
                        "title": "[WZ4004] Methods of Research in Forest and Wood Science"
                    },
                    "WZ4005": {
                        "module_id": "WZ4005",
                        "ects": 5.0,
                        "weighting_factor": 1.0,
                        "title": "[WZ4005] Lecture Series"
                    }
                },
                "Required Elective Optional Courses" : {...},
                "WZ4001": {...},
                "WZ4002": {...}
    }
 
Modules of a degree version (flattened curriculum):

    http://107.173.251.156:5000/modules?pStpStpNr=292?language=english
    
    {
        "modules": [
            {
                "module_id": "WZ4004",
                "ects": 5.0,
                "weighting_factor": 1.0,
                "title": "[WZ4004] Methods of Research in Forest and Wood Science"
            },
            {...},
            {...},
            ...
        ]
    }

Specific module of a degree version:

    http://107.173.251.156:5000/module?pStpStpNr=292&module_id=WZ4004&language=english

    {
        "module_id": "WZ4004",
        "ects": 5.0,
        "weighting_factor": 1.0,
        "title": "[WZ4004] Methods of Research in Forest and Wood Science"
    }

Degree versions which contain a given module (sorted):
    
    http://107.173.251.156:5000/parents?module_id=WZ4004&language=english

    {
        "pStpStpNrs": [
            292
        ]
    }

All versions of a degree (sorted):

    http://107.173.251.156:5000/degrees?degree_id=16_751&language=english

    {
        "pStpStpNrs": [
            292
        ]
    }
