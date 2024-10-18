#Define variables here first to be passed to sub modules
variable "SUMOLOGIC_ACCESS_ID" {
  type        = string
  description = "Sumo Logic Access ID"
  sensitive   = true
}

variable "SUMOLOGIC_ACCESS_KEY" {
  type        = string
  description = "Sumo Logic Access Key"
  sensitive   = true
}

#Define detectoins that you want to use and with what variables from root main.tf
module "tf-logs-monitor" {
  source               = "./detections/tf-logs-monitor/"
  SUMOLOGIC_ACCESS_ID  = var.SUMOLOGIC_ACCESS_ID
  SUMOLOGIC_ACCESS_KEY = var.SUMOLOGIC_ACCESS_KEY
}

module "tf-winevent-new-useradded" {
  source               = "./detections/tf-winevent-new-useradded/"
  SUMOLOGIC_ACCESS_ID  = var.SUMOLOGIC_ACCESS_ID
  SUMOLOGIC_ACCESS_KEY = var.SUMOLOGIC_ACCESS_KEY
}