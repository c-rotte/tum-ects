**1) Clone the repository** 

    git clone https://github.com/rchr1/tum-ects.git
    cd tum-ects
    
**2) Create and run the containers**

    docker-compose up

The api will be available at `localhost:5000`. The parser needs a few hours to collect all degrees.

**Exemplary call:**

    http://107.173.251.156:5000/module?degree_id=11_800&module_id=WZ2755
    
    {
    
       "module_id": "WZ2755",
       "title": {
           "german": "[WZ2755] Allgemeine Volkswirtschaftslehre",
           "english": "[WZ2755] Introduction to Economics"},
       "ects": 3.0,
       "weighting_factor": 1.0
    
    }
    
    
 

