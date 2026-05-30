# Commands

conda activate env_rl_project       
pip install -r requirements.txt
pip freeze > requirements.txt    
conda env export > environment.yml

docker build -t myimage .