# Outputs for the sample Terraform configuration

output "resource_group_name" {
  description = "The name of the created resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "The location of the created resource group"
  value       = azurerm_resource_group.main.location
}

output "virtual_machine_name" {
  description = "The name of the operations virtual machine"
  value       = azurerm_linux_virtual_machine.ops_vm.name
}

output "virtual_machine_size" {
  description = "The size of the operations virtual machine"
  value       = azurerm_linux_virtual_machine.ops_vm.size
}

output "virtual_machine_public_ip" {
  description = "The public IP address of the operations virtual machine"
  value       = azurerm_public_ip.ops_vm.ip_address
}

output "storage_account_name" {
  description = "The name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "virtual_network_name" {
  description = "The name of the virtual network"
  value       = azurerm_virtual_network.main.name
}

output "subnet_name" {
  description = "The name of the subnet"
  value       = azurerm_subnet.main.name
}
