variable "name" {}
variable "region" {}
variable "my_ip" {}
variable "public_key" {}
terraform {
  required_providers { azurerm = { source = "hashicorp/azurerm" } }
}
provider "azurerm" { features {} } # credentiale: ARM_* din mediu
resource "azurerm_resource_group" "rg" {
  name     = var.name
  location = var.region
}
resource "azurerm_virtual_network" "vn" {
  name                = var.name
  address_space       = ["10.0.0.0/16"]
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
}
resource "azurerm_subnet" "sn" {
  name                 = "default"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vn.name
  address_prefixes     = ["10.0.1.0/24"]
}
resource "azurerm_public_ip" "pip" {
  name                = var.name
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}
resource "azurerm_network_security_group" "nsg" {
  name                = var.name
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  security_rule {
    name                       = "ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
  }
}
resource "azurerm_network_interface" "nic" {
  name                = var.name
  location            = var.region
  resource_group_name = azurerm_resource_group.rg.name
  ip_configuration {
    name                          = "ip"
    subnet_id                     = azurerm_subnet.sn.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }
}
resource "azurerm_network_interface_security_group_association" "a" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}
resource "azurerm_linux_virtual_machine" "vm" {
  name                            = var.name
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = var.region
  size                            = "Standard_B1s"
  admin_username                  = "ubuntu"
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.nic.id]
  admin_ssh_key {
    username   = "ubuntu"
    public_key = var.public_key
  }
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }
}
output "public_ip" { value = azurerm_public_ip.pip.ip_address }
