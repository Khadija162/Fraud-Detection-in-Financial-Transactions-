terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
  }
}
variable "subscription_id" { type = string }
variable "region" { type = string, default = "northeurope" }
variable "storage_name" { type = string }
provider "azurerm" { features {} subscription_id = var.subscription_id }
resource "azurerm_resource_group" "fraud" { name = "fraud-platform-demo-rg" location = var.region }
resource "azurerm_storage_account" "lake" {
  name = var.storage_name
  resource_group_name = azurerm_resource_group.fraud.name
  location = azurerm_resource_group.fraud.location
  account_tier = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled = true
  min_tls_version = "TLS1_2"
}
resource "azurerm_storage_data_lake_gen2_filesystem" "lake" {
  name = "fraudlake"
  storage_account_id = azurerm_storage_account.lake.id
}
output "storage_account_name" { value = azurerm_storage_account.lake.name }
