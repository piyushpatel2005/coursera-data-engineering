resource "random_id" "master_password" {
  byte_length = 8
}

resource "aws_db_subnet_group" "database" {
  name       = "${var.project}-db-subnet-group"
  subnet_ids = [data.aws_subnet.private_subnet_a.id, data.aws_subnet.private_subnet_b.id]
}

resource "aws_db_instance" "database" {
  identifier                   = "${var.project}-db"
  instance_class               = "db.t3.micro" # Use the db.t3.micro instance type
  allocated_storage            = 20
  storage_type                 = "gp2"
  db_subnet_group_name         = aws_db_subnet_group.database.name # Use the db subnet group you created above
  vpc_security_group_ids       = [aws_security_group.database.id]
  performance_insights_enabled = true

  engine         = "postgres"
  engine_version = "15"

  port     = 5432
  db_name  = "postgres"
  username = var.db_master_username       # Use the master username variable
  password = random_id.master_password.id # Use the master password generated above

  publicly_accessible = false
  skip_final_snapshot = true
}

data "aws_db_instance" "database" {
  db_instance_identifier = aws_db_instance.database.id
}

