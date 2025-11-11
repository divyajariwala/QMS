resource "random_password" "aurora_master_password" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "aurora_master" {
  name       = "${var.short_name}-${var.environment}-aurora-postgres-master"
}

resource "aws_secretsmanager_secret_version" "aurora_master" {
  secret_id = aws_secretsmanager_secret.aurora_master.id
  depends_on = [aws_rds_cluster.rds_cluster]
  secret_string = jsonencode({
    username            = "postgres"
    password            = random_password.aurora_master_password.result
    engine              = "postgres"
    host                = aws_rds_cluster.rds_cluster.endpoint
    port                = 5432
    dbname              = "qms"
    dbClusterIdentifier = aws_rds_cluster.rds_cluster.id
  })

}

resource "aws_db_subnet_group" "subnet_group" {
  name       = "${var.short_name}-${var.environment}-db-subnet-group"
  subnet_ids = [var.subnet1, var.subnet2. var.subnet3, var.subnet4]
}

resource "aws_rds_cluster" "rds_cluster" {
  cluster_identifier                  = "${var.short_name}-${var.environment}-aurora-cluster"
  engine                               = "aurora-postgresql"
  engine_version                       = "15.4"
  database_name                        = "qms"
  master_username                      = "postgres"
  master_password                      = random_password.aurora_master_password.result

  db_subnet_group_name                 = aws_db_subnet_group.subnet_group.name
  vpc_security_group_ids               = [var.security_group_id]

  storage_encrypted                    = true

  backup_retention_period              = "7"
  copy_tags_to_snapshot                = true
  deletion_protection                  = true
  apply_immediately                    = true

  serverlessv2_scaling_configuration {
    min_capacity = var.serverless_min_acu
    max_capacity = var.serverless_max_acu
  }
}

resource "aws_rds_cluster_instance" "cluster_instance" {
  identifier          = "${var.short_name}-${var.environment}-aurora-cluster-instance-1"
  cluster_identifier  = aws_rds_cluster.rds_cluster.id
  engine              = aws_rds_cluster.rds_cluster.engine
  engine_version      = aws_rds_cluster.rds_cluster.engine_version
  instance_class      = "db.serverless"

  publicly_accessible = false
  db_subnet_group_name = aws_db_subnet_group.subnet_group.name
  apply_immediately = true
}