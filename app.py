import os
import boto3
from flask import Flask, render_template_string

app = Flask(__name__)

# Fetch AWS credentials from environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION") or None

# Initialize Boto3 clients with try/except
ec2_client=None
elb_client=None

if AWS_DEFAULT_REGION:
    try:
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_DEFAULT_REGION
        )
        ec2_client = session.client("ec2")
        elb_client = session.client("elbv2")
        print("[INFO] AWS clients initialized")
    except Exception as e:
        print(f"[WARNING] Failed to initialize AWS clients: {e}")
else:
    print("[INFO] AWS region is not provided. Skipping AWS client initialization")


@app.route("/")
def home():
    instance_data, vpc_data, subnet_data, lb_data, ami_data = [], [], [], [], []

    # Fetch EC2 instances
    if ec2_client:
        try:
            instances = ec2_client.describe_instances()
            for reservation in instances["Reservations"]:
                for instance in reservation["Instances"]:
                    # Default name
                    name = "N/A"
                    # Look for the 'Name' tag
                    for tag in instance.get("Tags", []):
                        if tag.get("Key") == "Name":
                            name = tag.get("Value")
                            break
                
                    instance_data.append({
                        "Name": name,
                        "ID": instance["InstanceId"],
                        "State": instance["State"]["Name"],
                        "Type": instance["InstanceType"],
                        "Public IP": instance.get("PublicIpAddress", "N/A")
                    })
        except Exception as e:
            print(f"Error fetching EC2 instances: {e}")

        # Fetch VPCs
        try:
            vpcs = ec2_client.describe_vpcs()
            vpc_data = [{"VPC ID": vpc["VpcId"], "CIDR": vpc["CidrBlock"]} for vpc in vpcs["Vpcs"]]
        except Exception as e:
            print(f"Error fetching VPCs: {e}")
            
        # Fetch subnets
        try:
            subnets = ec2_client.describe_subnets()
            subnet_data = [{"Subnet ID": subnet["SubnetId"],"VPC ID": subnet["VpcId"],"CIDR": subnet["CidrBlock"],"Availability Zone": subnet["AvailabilityZone"]} for subnet in subnets["Subnets"]]
        except Exception as e:
            print(f"Error fetching Subnets: {e}")
            
        # Fetch AMIs
        try:
            amis = ec2_client.describe_images(Owners=['self'])
            ami_data = [{"AMI ID": ami["ImageId"], "Name": ami.get("Name", "N/A")} for ami in amis["Images"]]
        except Exception as e:
            print(f"Error fetching AMIs: {e}")

    # Fetch Load Balancers
    if elb_client:
        try:
            lbs = elb_client.describe_load_balancers()
            lb_data = [{"LB Name": lb["LoadBalancerName"], "DNS Name": lb["DNSName"]} for lb in lbs["LoadBalancers"]]
        except Exception as e:
            print(f"Error fetching Load Balancers: {e}")

    # Render the result in a simple table
    html_template = """
    <html>
    <head>
        <title>AWS Resources</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f6fa;
                color: #2c3e50;
                margin: 20px;
                display: flex;
                justify-content: center;
            }

            .container {
                max-width: 900px;
                width: 100%;
            }

            /* Header */
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 30px;
            }

            .header-left img,
            .header-right img {
                max-width: 130px;
                height: auto;
            }

            .header-center h1 {
                font-size: 2.5em;
                color: #34495e;
                margin: 0;
                border-bottom: 3px solid #2980b9;
                padding-bottom: 5px;
                text-align: center;
            }

            h1 {
                color: #34495e;
                border-bottom: 3px solid #2980b9;
                padding-bottom: 5px;
                font-size: 1.5em;
                margin-top: 35px;
            }

            .table-wrapper {
                overflow-x: auto;
                margin-bottom: 30px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                min-width: 400px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border: 1px solid #bdc3c7;
            }

            th, td {
                padding: 6px 10px;
                text-align: left;
                font-size: 0.9em;
                border: 1px solid #bdc3c7;
            }

            th {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
            }

            tr:nth-child(even) {
                background-color: #ecf0f1;
            }

            tr:hover {
                background-color: #d6eaf8;
            }

            /* EC2 status badges */
            .status {
                padding: 3px 7px;
                border-radius: 12px;
                color: white;
                font-weight: bold;
                font-size: 0.85em;
            }
            .running { background-color: #27ae60; }
            .stopped { background-color: #c0392b; }
            .pending { background-color: #f39c12; }

            @media (max-width: 600px) {
                .header {
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                }
                .header-left, .header-right {
                    margin: 10px 0;
                }
            }
        </style>
    </head>
    <body>
    <div class="container">

        <!-- Header -->
        <div class="header">
            <div class="header-left">
                <img src="{{ url_for('static', filename='aws.png') }}" alt="AWS Logo">
            </div>
            <div class="header-center">
                <h1>AWS Resource Viewer</h1>
            </div>
            <div class="header-right">
                <img src="{{ url_for('static', filename='docker.svg') }}" alt="Docker Logo">
            </div>
        </div>

        <h1>Running EC2 Instances</h1>
        <div class="table-wrapper">
            <table>
                <tr>
                    <th>Name</th>
                    <th>ID</th>
                    <th>State</th>
                    <th>Type</th>
                    <th>Public IP</th>
                </tr>
                {% for instance in instance_data %}
                <tr>
                    <td>{{ instance['Name'] }}</td>
                    <td>{{ instance['ID'] }}</td>
                    <td>
                        <span class="status {% if instance['State'] == 'running' %}running{% elif instance['State'] == 'stopped' %}stopped{% else %}pending{% endif %}">
                            {{ instance['State'] }}
                        </span>
                    </td>
                    <td>{{ instance['Type'] }}</td>
                    <td>{{ instance['Public IP'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- VPCs -->
        <h1>VPCs</h1>
        <div class="table-wrapper">
            <table>
                <tr><th>VPC ID</th><th>CIDR</th></tr>
                {% for vpc in vpc_data %}
                <tr>
                    <td>{{ vpc['VPC ID'] }}</td>
                    <td>{{ vpc['CIDR'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- Subnets -->
        <h1>Subnets</h1>
        <div class="table-wrapper">
            <table>
                <tr><th>Subnet ID</th><th>VPC ID</th><th>CIDR</th><th>Availability Zone</th></tr>
                {% for subnet in subnet_data %}
                <tr>
                    <td>{{ subnet['Subnet ID'] }}</td>
                    <td>{{ subnet['VPC ID'] }}</td>
                    <td>{{ subnet['CIDR'] }}</td>
                    <td>{{ subnet['Availability Zone'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- Load Balancers -->
        <h1>Load Balancers</h1>
        <div class="table-wrapper">
            <table>
                <tr><th>LB Name</th><th>DNS Name</th></tr>
                {% for lb in lb_data %}
                <tr>
                    <td>{{ lb['LB Name'] }}</td>
                    <td>{{ lb['DNS Name'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- AMIs -->
        <h1>Available AMIs</h1>
        <div class="table-wrapper">
            <table>
                <tr><th>AMI ID</th><th>Name</th></tr>
                {% for ami in ami_data %}
                <tr>
                    <td>{{ ami['AMI ID'] }}</td>
                    <td>{{ ami['Name'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

    </div>
    </body>
    </html>
    """

    return render_template_string(html_template, 
                                  instance_data=instance_data, 
                                  vpc_data=vpc_data,
                                  subnet_data=subnet_data, 
                                  lb_data=lb_data, 
                                  ami_data=ami_data
                                  )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
