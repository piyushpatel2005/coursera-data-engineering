import json  # To read the JSON config file
import re  # To look for templated variables
from pathlib import Path  # To handle paths
import os

# Render the template
from jinja2 import (
    StrictUndefined,
    Template,
    UndefinedError,
)

def main():
    """Generates dag files based on the template.

    How to run the script: python generate_dags.py"""
    # Load the template
    with open("./template.py", "r", encoding="utf-8") as file:
        unsafe_template_str = file.read()

    folder_configs = Path("./dag_configs/")
    print(f"folder_configs {folder_configs}")
    
    dags_dir = "./../dags"
    
    if not os.path.exists(dags_dir):
        os.mkdir(dags_dir)
    else:
        print(f"The directory {dags_dir} already exists.")
    
    # For each JSON path that matches the pattern "config_*.json"
    for path_config in folder_configs.glob("config_*.json"):
        # Read configuration
        with open(path_config, "r", encoding="utf-8") as file:
            config = json.load(file)

        # Adds placeholders to avoid trying to replace Jinja expressions not 
        # defined in config files.
        template_str = protect_undefineds(unsafe_template_str, config)
        
        # Output filename
        filename = f"./../dags/{config['dag_name']}.py"
        
        # Replace the template_str with the config dictionary
        content = Template(template_str).render(config)
        
        # Write the file
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(content)
            print(f"Created {filename} from config: {path_config.name}...")
        

def protect_undefineds(template_str: str, config: dict):
    """Protects undefined jinja2 expressions by treating them as raw with placeholders.

    This function is useful if you want to avoid replacing a Jinja expression. For instance:
    `{{ data_interval_end }}` is defined while running your DAG, not in the config files.

    Args:
        template_str (str): template in string format
        config (dict): values defined to be replaced in the jinja2 expression.

    Returns:
        str: template_str with undefined parameters protected as raw text (% raw %).
    """
    pattern = re.compile(r"(\{\{[^\{]*\}\})")
    for j2_expression in set(pattern.findall(template_str)):
        try:
            Template(j2_expression, undefined=StrictUndefined).render(config)
        except UndefinedError:
            template_str = template_str.replace(
                j2_expression, f"{{% raw %}}{j2_expression}{{% endraw %}}"
            )
    return template_str


if __name__ == "__main__":
    main()
