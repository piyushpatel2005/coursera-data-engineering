data "aws_vpc" "main" {
  id = var.vpc_id
}

# Create a data source for the public subnet in
# the AZ A using the corresponding variable
data "aws_subnet" "public_subnet_a" {
  id = var.public_subnet_a_id
}

# Create a data source for the public subnet in
# the AZ B using the corresponding variable
data "aws_subnet" "public_subnet_b" {
  id = var.public_subnet_b_id
}

# Create a data source for the private subnet in
# the AZ A using the corresponding variable
data "aws_subnet" "private_subnet_a" {
  id = var.private_subnet_a_id
}

# Create a data source for the private subnet in
# the AZ B using the corresponding variable
data "aws_subnet" "private_subnet_b" {
  id = var.private_subnet_b_id
}

### END CODE HERE ###

resource "aws_security_group" "bastion_host" {
  vpc_id = data.aws_vpc.main.id
  name   = "${var.project}-bastion-host-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow incoming SSH connections (Linux)"
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outgoing traffic"
  }

  tags = {
    Name = "${var.project}-bastion-host-sg"
  }
}

resource "aws_security_group" "database" {
  vpc_id = data.aws_vpc.main.id
  name   = "${var.project}-database-sg"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion_host.id]
    description     = "Allow incoming connections from the bastion host sg"
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outgoing traffic"
  }

  tags = {
    Name = "${var.project}-database-sg"
  }
}
