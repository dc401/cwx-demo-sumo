#### Provider inherit detailsf rom root main.tf ####
terraform {
  required_providers {
    sumologic = {
      source  = "SumoLogic/sumologic"
      version = "2.31.5"
    }
  }
}

# Setup authentication variables. See "Authentication" section for more details.
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

# Configure the Sumo Logic Provider
provider "sumologic" {
  access_id   = var.SUMOLOGIC_ACCESS_ID
  access_key  = var.SUMOLOGIC_ACCESS_KEY
  environment = "us2"
}

#### USE CASE STARTS HERE ####

resource "sumologic_monitor" "tf-winevent-new-useradded" {
  name                      = "tf-winevent-new-useradded"
  description               = "New local user added to a Windows host."
  type                      = "MonitorsLibraryMonitor"
  is_disabled               = false
  monitor_type              = "Logs"
  evaluation_delay          = "0m"
  notification_group_fields = ["_sourcehost"]

  #track and group for future TTP management

  tags = {
    "ttp"       = "T1136.001"
    "logsource" = "winevent"
    "owner"     = "secops"
  }

  #sumo logic requires double quotes in string fields. hcl requires double quotes as well. use escapes.
  queries {
    row_id = "A"
    query  = "_sourceName=Security | where eventid = \"4720\" | where %\"provider.name\" = \"Microsoft-Windows-Security-Auditing\""
  }

  trigger_conditions {
    logs_static_condition {
      warning {
        time_range = "-15m"
        alert {
          threshold      = 0
          threshold_type = "GreaterThan"
        }
        resolution {
          threshold         = 0
          threshold_type    = "LessThanOrEqual"
          resolution_window = "15m"
        }
      }
    }
  }
  notifications {
    notification {
      connection_type = "Email"
      recipients = [
        "REPLACE@xtecsystems.com",
      ]
      subject      = "Monitor Alert: {{TriggerType}} on {{Name}}"
      time_zone    = "CST"
      message_body = "Triggered {{TriggerType}} Alert on {{Name}}: {{QueryURL}}"
    }
    run_for_trigger_types = ["Warning"]
  }

}