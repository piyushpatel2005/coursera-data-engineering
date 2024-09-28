data "aws_subnet" "private_a" {
  id = var.private_subnet_a_id
}

data "aws_security_group" "db_sg" {
  id = var.db_sg_id
}
