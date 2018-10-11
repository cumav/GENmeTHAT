# Generate random names

### How to use (without frontend)
* Docker has to be installed.
* Run ```docker build -t genmethat:namegen .``` in the genme folder. This will create the docker image.
* To start the image run ```docker run -p 8000:8000 genmethat:namegen```. Now you can start making requests.
* To check if everything is running visit: ```http://localhost:8000/api/load_model/```. It should say: "successfully loaded model."


### Requests:

POST Requests:
    
    - Training:
        URL: localhost:8000/api/train/
        JSON-Body: {
                        "data": "this,is,comma,seperated,data",
                        "category": "names"
                    }
    - Load last trained model:
        URL: localhost:8000/api/load_model/
    - Generate names:
        URL: http://localhost:8000/api/generate/?spread=4
        (Bigger spread == more random)
