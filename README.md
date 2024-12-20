# spatial_data_api
Basic CRUD application allowing to interact with so called "Projects".

## How to run it
### Initial build + running the container
For initial build and setting up, use `docker-compose up --build` 
in the root directory of the project.

For the headless run use `docker-compose up -d --build` command

### Running the container
After you've performed initial build, you can use `docker-compose up` in the root directory of the project
to start it up with the process attached to your window.

To run the project in the headless mode use `docker-compose up -d`

## Interaction
To learn what API endpoints are available and how each one of them can be used, 
access the API docs http://localhost/docs#/ once the container is up and running