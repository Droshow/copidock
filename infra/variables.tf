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