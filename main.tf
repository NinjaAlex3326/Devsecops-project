variable "name" {}
variable "region" {}
variable "my_ip" {}
variable "public_key" {}
provider "aws" { region = var.region }
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}
resource "aws_key_pair" "k" {
  key_name   = var.name
  public_key = var.public_key
}
resource "aws_security_group" "sg" {
  name = var.name
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.my_ip}/32"] # SSH doar de la IP-ul tau
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_instance" "vm" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.k.key_name
  vpc_security_group_ids = [aws_security_group.sg.id]
  metadata_options { http_tokens = "required" }
  root_block_device { encrypted = true }
  tags = { Name = var.name }
}
output "public_ip" { value = aws_instance.vm.public_ip }
