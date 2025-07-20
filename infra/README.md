# Terraform S3 Bucket Provisioning

This project contains Terraform configurations for provisioning an S3 bucket in AWS, along with a GitHub Actions workflow to automate the deployment process.

## Project Structure

```
terraform-s3-bucket
├── .github
│   └── workflows
│       └── terraform.yml      # GitHub Actions workflow for Terraform
├── terraform
│   ├── main.tf                 # Main Terraform configuration for S3 bucket
│   ├── variables.tf            # Input variables for Terraform configuration
│   └── outputs.tf              # Output values for Terraform configuration
└── README.md                   # Project documentation
```

## Prerequisites

- AWS account
- Terraform installed on your local machine
- GitHub repository to host the project

## Setup Instructions

1. **Clone the Repository**
   Clone this repository to your local machine using:
   ```
   git clone <repository-url>
   ```

2. **Configure AWS Credentials**
   Ensure that your AWS credentials are configured. You can set them up using the AWS CLI:
   ```
   aws configure
   ```

3. **Modify Variables**
   Edit the `variables.tf` file to set any necessary variables for your S3 bucket configuration.

4. **Initialize Terraform**
   Navigate to the `terraform` directory and run:
   ```
   terraform init
   ```

5. **Apply Terraform Configuration**
   To create the S3 bucket, run:
   ```
   terraform apply
   ```

6. **Check Outputs**
   After the apply command completes, check the outputs defined in `outputs.tf` for information about the created resources.

## GitHub Actions Workflow

The GitHub Actions workflow defined in `.github/workflows/terraform.yml` will automatically apply the Terraform configurations when changes are pushed to the repository. Ensure that the workflow is properly configured with the necessary AWS credentials in your GitHub repository secrets.

## License

This project is licensed under the MIT License. See the LICENSE file for details.