# 3. Provideri cloud

## AWS
Creeaza un utilizator IAM cu drepturi EC2 si pune in `.env`: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`. Foloseste `t3.micro` (free tier la conturi noi).

## Azure
`az ad sp create-for-rbac --role Contributor --scopes /subscriptions/<ID>` apoi in `.env`: `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_TENANT_ID`, `ARM_SUBSCRIPTION_ID`.

## OCI (Oracle)
Ruleaza `oci setup config` si monteaza `~/.oci` in container. Seteaza in `.env`: `TF_VAR_compartment_ocid`, `TF_VAR_subnet_ocid`, `TF_VAR_image_ocid` (Ubuntu aarch64), `TF_VAR_availability_domain`. Shape-ul A1.Flex este Always Free.

## VM-urile clientilor
Foloseste "Adauga VM existent". Cere clientului sa adauge cheia ta **publica** in `~/.ssh/authorized_keys` pe un user dedicat. Nu cere niciodata parola sau cheia lui privata, si pastreaza un acord scris cu limitele accesului.
