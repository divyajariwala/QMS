# resource "aws_security_group" "lambda_security_group" {
#   name  = "${var.short_name}-${var.environment}-${var.component}-lambda-security-group"
#   description = "lambda-security-group"
#   vpc_id = var.vpc_id
# }

# resource "aws_security_group_rule" "lambda_egress_443" {
#   type = "egress"
#   from_port = "443"
#   to_port = "443"
#   protocol = "tcp"
#   security_group_id = "aws_security_group.lambda_security_group.id"
#   cidr_blocks = ["0.0.0.0/0"]
# }

# resource "aws_security_group_rule" "lambda_egress_80" {
#   type = "egress"
#   from_port = "80"
#   to_port = "80"
#   protocol = "tcp"
#   security_group_id = aws_security_group.lambda_security_group.id
#   cidr_blocks = ["0.0.0.0/0"]
# }

# resource "aws_security_group" "ecs_sg" {
#   name = "ecs-security-group"
#   description = "Allow HTTP inbound traffic"
#   vpc_id = aws_vpc.main_vpc.id
#   ingress {
#     from_port = 80
#     to_port = 80
#     protocol = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }