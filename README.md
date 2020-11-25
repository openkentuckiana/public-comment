Public Comment
===============

[![Build Status](https://travis-ci.com/codeforkyana/public-comment.svg?branch=main)](https://travis-ci.com/codeforkyana/public-comment)
[![codecov](https://codecov.io/gh/codeforkyana/public-comment/branch/main/graph/badge.svg?token=CMU18CN6CP)](https://codecov.io/gh/codeforkyana/public-comment)


[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/codeforkyana/public-comment)

About
-----------------
This application is built to allow organizations to solicit public comments on federal regulations posted to [regulations.gov](https://www.regulations.gov/).

Reviewing and responding to public comments regarding proposed regulations is a core step in the process of making and finalizing regulations that can affect almost every aspect of our lives. Making it easier to increase both the quantity and quality of the comments Americans provide to our agencies will improve outcomes and will often help litigators defend against harmful changes to agency regulations.

Furthermore, this tool helps organizations who are encouraging their membership and the public to provide comments identify and build relationships with those people in their communities that care most about a particular subject. Over time, using a tool like this will help organizations build grassroots power if they invest in developing and deepening those relationships.

Organizations often have campaigns to get citizens to either support or oppose a proposed federal regulation. These campaigns have historically worked in a few ways:

* The organization collects comments from the public and manually submits them to regulations.gov
* The organization directs the public to regulations.gov and asks them to submit comments on their own
* Organization pay for software to facilitate this process

Each of these have their downsides, particularly for small nonprofits.

* Manual collection is time consuming and error prone and doesn't result in a unified record of public participation
* Asking the public to use regulations.gov is more challenging for the user and removes the nonprofit from the process
* Commercial software is often expensive

Regulations.gov currently does not have a way to submit comments, but a new API that supports this functionality is currently in the works. It was supposed to be 

The API documentation is here: https://open.gsa.gov/api/regulationsgov/

The most recent communication about the status of this API from the eRulemaking team is:

> We had previously communicated our plans to cutover to the new API in November 2020.  At this time a release date for the v4 API is unavailable. The target date will be socialized by the program office in the near future, providing more clarity on the plans to complete the configuration and development.
>
> We continue to appreciate everyone’s feedback on the new Regulations.gov API draft documentation.  We are making updates to reflect comments received.  Most notably, we added frequently asked questions. Additional functionality, including bulk download and pagination limits, will be addressed before v3 retirement.  We aim to give you sufficient time to transition to our short term bulk download solution.
>
> The new API (version 4) has been developed in conjunction with a new version of Regulations.gov, now in beta status at https://beta.regulations.gov/. The new API (version 4) is still being finalized, and will replace the current API (version 3) as part of a planned forthcoming website transition.  

Goals
-----------------
The goals of this project are:

* Provide an easy to use web interface for organizations to be able to use set up comment collection forms
* Allow simple customizations of those forms
* Capture information about users submitting comments for later use by the organizations
* Reliably submit comments to regulations.gov
* Be easy to run by organizations or Code for America brigades  

MVP
-----------------
The last step to getting a minimum viable product (MVP) up and running. Most of the basic functionality exists, with the exception of this piece.  

Contributing
-----------------
This project has a variety of needs, from product management to design to software devlopment. If you'd like to help out, reach out via the 
`#code-for-kentuckiana` channel in [Code for America's Slack](http://slack.codeforamerica.org/).

See [Contributing](./docs/CONTRIBUTING.md) for more info.

Deploying
-----------------
See [Deploying](./docs/DEPLOYING.md) for more info.
