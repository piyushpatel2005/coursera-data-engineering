# Week 1 Assignment: Graph Databases and Vector Search with Neo4j


- Click on Create environment, type in the name de-c3w1a1.
- Scroll down and choose t3.small in the instance type.
- In networking settings, make sure to click on Secure Shell (SSH) otherwise your instance will not be accessible.
- Click on the VPC settings dropdown, choose the VPC named de-c3w1a1.
- For the subnet, select the public one: de-c3w1a1-public-subnet-a (or you can also choose de-c3w1a1-public-subnet-b).
- Click on Create button.
- Wait for the environment to be created which migh
- Use the following command (you can copy and paste it) in the terminal to download the required files for the lab:

`aws s3 cp --recursive s3://dlai-data-engineering/labs/c3w1a1-792315/ ./`

- Run the following command to start the Jupyter Lab service in a virtual environment:

 `source scripts/setup_jupyter_env.sh`

- Open the notebook [C3_W1_Assignment.ipynb](C3_W1_Assignment_Solution.md) and follow the instructions there.