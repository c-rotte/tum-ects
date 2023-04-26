# TUM ECTS

A simple FastAPI application to manage TUM degrees, modules, and mappings.

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
2. Get the info of a specific degree:
```bash
GET http://localhost:5000/degree?degree_id=<degree_id>
```
3. Get the info of a specific module:
```bash
GET http://localhost:5000/module?module_id=<module_id>
```
4. Get the modules of a degree:
```bash
GET http://localhost:5000/modules_of_degree?degree_id=<degree_id>[&valid_from=<valid_from>&valid_to=<valid_to>&degree_version=<degree_version>]
```