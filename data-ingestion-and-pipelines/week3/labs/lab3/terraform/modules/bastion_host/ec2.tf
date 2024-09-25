resource "tls_private_key" "bastion_host_key_pair" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "ssh_key" {
  filename        = "${aws_key_pair.bastion_host_key_pair.key_name}.pem"
  content         = tls_private_key.bastion_host_key_pair.private_key_pem
  file_permission = "0400"
}


data "aws_ami" "latest_ami" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server-*"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

### START CODE HERE ### (~ 21 lines of code)

# Create an AWS key pair, associating the public
# key you created in the first resource in this file
resource "aws_key_pair" "bastion_host_key_pair" {
  key_name   = "${var.project}-bastion-host-key"
  public_key = tls_private_key.bastion_host_key_pair.public_key_openssh
}

# Complete the configuration for the EC2 instance
# for the bastion host
resource "aws_instance" "bastion_host" {
  ami                         = data.aws_ami.latest_ami.id
  instance_type               = "t3.nano"                                   # Use the t3.nano instance type
  key_name                    = aws_key_pair.bastion_host_key_pair.key_name # Associate the aws key pair you created above
  user_data                   = <<-EOF
    #!/bin/bash
    sudo apt-get update -y
    sudo apt install postgresql postgresql-contrib -y
    curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.deb.sh | sudo bash
    
    # Download and install Sysbench 1.0.20
    wget https://packagecloud.io/akopytov/sysbench/packages/ubuntu/bionic/sysbench_1.0.20-1_amd64.deb/download.deb -O sysbench_1.0.20-1_amd64.deb
    sudo dpkg -i sysbench_1.0.20-1_amd64.deb
    sudo apt --fix-broken install -y
    
    sudo apt install -y stress
    sudo apt install -y net-tools
    EOF
  user_data_replace_on_change = true

  subnet_id                   = data.aws_subnet.public_subnet_a.id   # Use the public subnet for AZ A
  vpc_security_group_ids      = [aws_security_group.bastion_host.id] # Use the security group you created for the bastion host
  associate_public_ip_address = true

  tags = {
    Name = "${var.project}-bastion-host"
  }
}

### END CODE HERE ###
