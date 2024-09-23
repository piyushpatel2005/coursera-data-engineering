resource "aws_db_subnet_group" "vector_db_subnet_group" {
  name = "${var.project}-vector-db-subnet-group"
  subnet_ids = [
    data.aws_subnet.public_a.id,
    data.aws_subnet.public_b.id
  ]
}


resource "aws_security_group" "vector_db_sg" {
  name        = "${var.project}-vector-db-sg"
  description = "Allow PostgreSQL connection to DB"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL port"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-vector-db-sg"
  }

}


resource "aws_db_instance" "master_db" {
  identifier            = "${var.project}-vector-db"
  allocated_storage     = 20
  max_allocated_storage = 0
  storage_type          = "gp2"
  engine                = "postgres"
  engine_version        = "16.2"
  port                  = 5432
  instance_class        = "db.t3.micro"
  db_name               = "postgres"
  username              = var.master_username
  password              = random_id.master_password.id
  publicly_accessible   = true
  skip_final_snapshot   = true
  db_subnet_group_name  = aws_db_subnet_group.vector_db_subnet_group.id
  vpc_security_group_ids = [
    aws_security_group.vector_db_sg.id
  ]
}

resource "random_id" "master_password" {
  byte_length = 8
}
