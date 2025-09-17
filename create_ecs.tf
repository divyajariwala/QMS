resource "aws_lb" "ecs_alb_internal" {
  name = "${var.short_name}-${var.environment}-api-int-alb"
  load_balancer_type = "application"
  internal = true
  security_groups = [var.security_group_id]
  subnets = [var.subnet1, var.subnet2]
}

resource "aws_lb_target_group" "ecs_alb_target_group" {
  name = "${var.short_name}-${var.environment}-api-alb-tg"
  port = 8080
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = var.vpc_id
}

resource "aws_lb_listener" "ecs_alb_listener" {
  load_balancer_arn = aws_lb.ecs_alb_internal.arn
  port = 80
  protocol = "HTTP"
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.ecs_alb_target_group.arn
  }
}

resource "aws_ecs_task_definition" "api_task_definition" {
  family = "${var.short_name}-api"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = "1024"
  memory = "3072"
  execution_role_arn = var.ecs_task_role_arn
  task_role_arn = var.ecs_task_role_arn
  lifecycle {
    create_before_destroy = true
  }
  container_definitions = jsonencode([
    {
      name = "${var.short_name}-api"
      image = "${var.api_image_uri}"
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort = 8080
          protocol = "tcp"
          name = "${var.short_name}-api"
        }
      ]
      environment = [
        {
          name = "API_KEY"
          value = "${var.ecs_openai_api_key}"
        },
        {
          name = "BASE_URL"
          value = "${var.ecs_openai_base_url}"
        },
        {
          name = "SAGEMAKER_ENDPOINT_NAME"
          value = "${var.sagemaker_endpoint_name}"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "${aws_cloudwatch_log_group.ecs_log_group.name}"
          awslogs-region = "${var.region}"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_cluster" "ecs_cluster" {
  name = "${var.short_name}-${var.environment}-ecs-cluster"
}

resource "aws_ecs_service" "ecs_service" {
  name = "${var.short_name}-${var.environment}-api"
  cluster = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.api_task_definition.arn
  launch_type = "FARGATE"
  network_configuration {
    subnets = [var.subnet1, var.subnet2, var.subnet3, var.subnet4]
    security_groups = [var.security_group_id]
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_alb_target_group.arn
    container_name = "${var.short_name}-api"
    container_port = 8080
  }
  desired_count = 1
}

resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name = "/ecs/${var.short_name}-${var.environment}-api"
  retention_in_days = 30

}
