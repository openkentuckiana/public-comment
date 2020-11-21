Deploying
===============

Overview
-----------------
The supported way to deploy `public-comment` is on [Heroku](https://www.heroku.com). Heroku is a platform as a service, which means they provide managed services that can be used to run applications. Things like server backups and upgrades are managed by Heroku.

Required Services
-----------------
* Email provider - used to send emails to organization users and commenters
* AWS S3 - used to store images uploaded by organizations (and in the future, documents that are submitted to regulations.gov)

See below on how to sign up for and configure these services.

Deploying to your Heroku account
-----------------
If you want to run your own instance of this application, you can easily deploy it to your Heroku account.

Start by clicking this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You'll need to fill in the required configuration variables, particularly the ones for your SMTP (email) provider and for S3.

You will also need to create an administrator account to use to log in:

- Navigate to your app in the Heroku console (e.g. `https://dashboard.heroku.com/apps/<APP NAME>`)
- Select `Run Console` from the `More` menu
- Enter `bash` and click `Run`
- Wait for the console to connect
- Run `./manage.py createsuperuser`
- Enter the required information
- Log in at [https://APP_NAME.herokuapp.com/admin/](https://APP_NAME.herokuapp.com/admin/) 

Configuration
-----------------

There are many options that can be configured via environment variables. Environment variables are called config vars in Heroku, and they can be set by following [Heroku's instructions](https://devcenter.heroku.com/articles/config-vars).

Environment Variable    | Description
------                  | ------
ALLOWED_HOSTS           | The server names that are allowed to connect to this app. [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts). Default: `.herokuapp.com`
AWS_ACCESS_KEY_ID       | AWS access key. [AWS Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey). See below for instructions on configuring S3.
AWS_SECRET_ACCESS_KEY   | AWS secret access key.
AWS_STORAGE_BUCKET_NAME | AWS S3 bucket where uploaded files are stored.
DEFAULT_FROM_EMAIL      | Email address used as the from address on emails sent from the app. [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email). Default: `webmaster@localhost`
DJANGO_DEBUG            | Set to `True` to enable debugging. This should not be `True` for a production app. Default: `False`
DJANGO_SETTINGS_MODULE  | The Django settings file to use. Default: `public_comment.settings.production`
EMAIL_HOST              | SMTP settings, see [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#email-host). See below for instructions on configuring SMTP with Sendgrid. Default: `smtp.sendgrid.net`
EMAIL_HOST_PASSWORD     | SMTP settings, see [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#email-host). Default: `''` (empty string)
EMAIL_HOST_USER         | SMTP settings, see [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#email-host). Default: `apikey`
EMAIL_PORT              | SMTP settings, see [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#email-host). Default: `587`
EMAIL_USE_SSL           | SMTP settings, see [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#email-host). Default: `False`
EMAIL_USE_TLS           | SMTP settings, see [Django documentation](https://docs.djangoproject.com/en/dev/ref/settings/#email-host). Default: `True`
NEW_RELIC_APP_NAME      | App name to use for identifying the app in [Newrelic](https://newrelic.com). Newrelic is optional. See below for more information. Default: `Public Commenter`
NEW_RELIC_ENVIRONMENT   | The environment to use from the `newrelic.ini` config. Default 'production'
NEW_RELIC_LICENSE_KEY   | License key to use with [Newrelic](https://newrelic.com). Newrelic is optional. If this value is empty, Newrelic will not be used. See below for more information. Default `''` (empty string)

Third Party Services
-----------------

### Required

#### SMTP
You may use any SMTP provider you would like, just follow the [Django instructions](https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend) and override the relevant settings.

Sendgrid is a reasonably-priced SMTP service. To use Sengrid:
1. Sign up for an account at https://sendgrid.com
1. Go to API Keys: https://app.sendgrid.com/settings/api_keys
1. Click `Create API Key`
1. Give the API key a name
1. Choose `Restricted Access`
1. Choose `Full Access` for `Mail Send`
1. Copy the API key you were given into the `EMAIL_HOST_PASSWORD` config var value in Heroku (the other email config values default to what Sendgrid needs)

#### AWS S3
S3 is required to allow organizations to upload images for their forms, thank you pages, and emails.

Create an AWS account:
1. Sign up for a new account at https://portal.aws.amazon.com/billing/signup#/start

Create a user that will be used to access the bucket:
1. Sign into AWS
1. Go to Identity and Access Management (IAM) Users: https://console.aws.amazon.com/iam/home#/users
1. Click `Add User`
1. Give the user a name
1. Check `Programmatic access`
1. Click `Next: Permissions`
1. Click `Next: Tags`
1. Click `Next: Review`
1. Click `Create User` (you can ignore the `This user has no permissions` warning)
1. Copy the `Access key ID` into the `AWS_ACCESS_KEY_ID` config var value in Heroku
1. Copy the `Secret access key` into the `AWS_SECRET_ACCESS_KEY` config var value in Heroku
1. Click `Close`
1. Click on the user in the list
1. Copy the `User ARN value`, you will need this when setting up the S3 bucket

Create an S3 bucket:
1. Sign into AWS
1. Go to the S3 screen: https://s3.console.aws.amazon.com/s3/home
1. Click `Create Bucket`
1. Give the bucket a name
1. Click the `Create bucket` button at the bottom of the screen
1. Click the bucket from the list of buckets to view its details
1. Click the `Permissions` tab
1. Click `Edit` under bucket policy
1. Paste the following policy:
    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "<USER ARN YOU COIPED>"
                },
                "Action": "s3:ListBucket",
                "Resource": "arn:aws:s3:::<YOUR BUCKET NAME>"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "<USER ARN YOU COIPED>"
                },
                "Action": [
                    "s3:DeleteObject",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:PutObjectAcl"
                ],
                "Resource": "arn:aws:s3:::<YOUR BUCKET NAME>/*"
            }
        ]
    ```
   Replace `<USER ARN YOU COIPED>` with the user ARN you copied above. It should look something like: `arn:aws:iam::97233373:user/my-new-user`.
   Replace `<YOUR BUCKET NAME>` with the name of your bucket. 
   This will allow the new user you created to add and remove items to your new bucket using the credentials you created earlier.
1. Click `Save changes`
1. Copy the name of your bucket into the `AWS_STORAGE_BUCKET_NAME` config var value in Heroku.

### Optional

#### Newrelic

[Newrelic](https://newrelic.com/) is an application monitoring service. It is a paid service, but Code for America brigades are eligible for a free account.

If an `NEW_RELIC_LICENSE_KEY` environment variable is set on Heroku, the app will try to launch with the Newrelic agent enabled.

To get a Newrelic license key:
1. Go to the Newrelic dashboard's API Keys section: https://one.newrelic.com/launcher/api-keys-ui.api-keys-launcher
1. Click `Create key`
1. Chose `Ingest - License` as the `Key type`
1. Give the key a name
1. Click `Create key`
1. Copy the name of your bucket into the `NEW_RELIC_LICENSE_KEY` config var value in Heroku.