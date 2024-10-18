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
  sensitive = true
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

resource "sumologic_monitor" "tf_logs_monitor_1" {
  name             = "Terraform Logs Monitor"
  description      = "tf logs monitor"
  type             = "MonitorsLibraryMonitor"
  is_disabled      = false
  content_type     = "Monitor"
  monitor_type     = "Logs"
  evaluation_delay = "5m"
  tags = {
    "team"        = "monitoring"
    "application" = "sumologic"
  }

  queries {
    row_id = "A"
    query  = "_sourceCategory=event-action info"
  }

  trigger_conditions {
    logs_static_condition {
      critical {
        time_range = "15m"
        alert {
          threshold      = 40.0
          threshold_type = "GreaterThan"
        }
        resolution {
          threshold      = 40.0
          threshold_type = "LessThanOrEqual"
        }
      }
    }
  }

  notifications {
    notification {
      connection_type = "Email"
      recipients = [
        "dchow@xtecsystems.com",
      ]
      subject      = "Monitor Alert: {{TriggerType}} on {{Name}}"
      time_zone    = "CST"
      message_body = "Triggered {{TriggerType}} Alert on {{Name}}: {{QueryURL}}"
    }
    run_for_trigger_types = ["Critical", "ResolvedCritical"]
  }

}