variable "name" {}
variable "region" {}
variable "my_ip" {}
variable "public_key" {}
# Setate prin TF_VAR_* in .env (vezi docs/03-providers.md)
variable "compartment_ocid" {}
variable "subnet_ocid" {}
variable "image_ocid" {}
variable "availability_domain" {}
provider "oci" { region = var.region } # auth din ~/.oci/config
resource "oci_core_instance" "vm" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain
  display_name        = var.name
  shape               = "VM.Standard.A1.Flex" # Always Free
  shape_config {
    ocpus         = 1
    memory_in_gbs = 6
  }
  source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }
  create_vnic_details {
    subnet_id        = var.subnet_ocid
    assign_public_ip = true
  }
  metadata = { ssh_authorized_keys = var.public_key }
}
output "public_ip" { value = oci_core_instance.vm.public_ip }
