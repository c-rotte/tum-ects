# TUM ECTS

A FastAPI application to manage TUM degrees, modules, and mappings. This application collects data from TUM Campus Online, crawls degree and module information, and provides a convenient API to access the data.

Note that the crawler may take approximately 7 to 8 hours to collect all degrees and their associated information.

## Database Scheme

![image](https://user-images.githubusercontent.com/54217818/235301806-33b5ef98-fec2-4dbc-a10e-aeee65dc167d.png)

## Instructions on how to run

### 1) Clone the repository
```bash
git clone https://github.com/rchr1/tum-ects.git
cd tum-ects
```

### 2) Create and run the containers
```bash
docker-compose up -d
```

The API will be available at `localhost:5000`. The crawler needs a few hours to collect all degrees.

## API Endpoints
1. Get the number of degrees and modules:
```bash
GET http://localhost:5000/
```
2. Get all degrees:
```bash
GET http://localhost:5000/degrees
```
3. Get the info of a specific degree:
```bash
GET http://localhost:5000/degree?degree_id=<degree_id>
```
4. Get the info of a specific module:
```bash
GET http://localhost:5000/module?module_id=<module_id>
```
5. Find a module by its number:
```bash
GET http://localhost:5000/find_module?nr=<module_number>
```
6. Get the modules of a degree:
```bash
GET http://localhost:5000/modules_of_degree?degree_id=<degree_id>[&valid_from=<valid_from>&valid_to=<valid_to>&degree_version=<degree_version>]
```
