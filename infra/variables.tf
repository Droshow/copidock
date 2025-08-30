variable "region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "eu-central-1"
}

variable "name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "copidock"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "enable_pitr" {
  description = "Enable point-in-time recovery for DynamoDB tables"
  type        = bool
  default     = false
}