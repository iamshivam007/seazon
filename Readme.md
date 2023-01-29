# Steps to setup

- Install Pyenv 
- - `sudo apt install curl -y`
- - `sudo apt install git -y`
- - `sudo apt update`
- - `curl https://pyenv.run | bash`
- - `export PATH="$HOME/.pyenv/bin:$PATH" && eval "$(pyenv init --path)" && echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc`
- Install Python runtime
- - `pyenv install 3.10.0`
- Setup Virtual
- - `pyenv virtualenv 3.10.0 seazon`
- - `pyenv activate seazon`
- Install requirements
- - `pip install -r requirements.txt`
- Copy `build/env.template.sh` to `build/env.sh` and update values
- - Run `source build/env.sh`
- Run migration
- Run server