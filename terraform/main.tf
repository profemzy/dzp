# Sample Terraform configuration for testing
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

# Create a simple local file
resource "local_file" "example" {
  content  = "Hello from DZP IAC Agent running in Docker!"
  filename = "${path.module}/hello.txt"
}

output "greeting" {
  value = "DZP IAC Agent is working! File created at: ${local_file.example.filename}"
}
