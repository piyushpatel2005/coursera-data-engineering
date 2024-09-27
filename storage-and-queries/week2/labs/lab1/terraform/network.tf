data "aws_vpc" "main" {
  id = var.vpc_id
}

data "aws_subnet" "private_a" {
  id = var.private_subnet_a_id
}
