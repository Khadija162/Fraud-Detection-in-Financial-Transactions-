terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
  }
}
provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
resource "azurerm_resource_group" "rg" {
  name = "${var.prefix}-rg"
  location = var.location
}
resource "azurerm_storage_account" "lake" {
  name = var.storage_account_name
  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  account_tier = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled = true
  min_tls_version = "TLS1_2"
}
resource "azurerm_storage_data_lake_gen2_filesystem" "lake" {
  name = "fraud-data"
  storage_account_id = azurerm_storage_account.lake.id
}
resource "azurerm_container_registry" "acr" {
  name = var.registry_name
  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  sku = "Basic"
  admin_enabled = false
}
resource "azurerm_log_analytics_workspace" "log" {
  name = "${var.prefix}-logs"
  location = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku = "PerGB2018"
  retention_in_days = 30
}
resource "azurerm_container_app_environment" "env" {
  name = "${var.prefix}-env"
  location = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id
}
# Secure image access via managed identity and AcrPull needs configuration before deploy.
# API is intentionally not exposed publicly by this example.
