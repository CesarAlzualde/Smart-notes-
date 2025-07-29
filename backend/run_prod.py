import app.__production_config 
from run import app 
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000) 
