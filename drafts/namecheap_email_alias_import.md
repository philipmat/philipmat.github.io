---
title: NameCheap Emails Alias Import
snippet: A script to import email aliases into NameCheap
layout: post
---

The reason you might want to use NameCheap to set up
email forwarders are discussed at the end of the article.

I'll assume that you landed on this post because you're
looking for the how, not necessarily the why. If so,
let's start first with the import script.

## Prerequisites

You'll need to:

1. download or checkout the script
   from [this GitHub Gist][import_script];
2. [obtain an API key][nc_api_key] from NameCheap;
3. create a config file
4. provide the script with a CSV file containing the list 
   of aliases for *one domain only*
   and their respective destinations

Wise, although not required, I recommend you
also sign up for a [NameCheap sandbox API key][nc_api_sandbox] 
and test the import script against that environment first.

### Creating a config file

You'll need a config file that tells the import program:

- What your NameCheap or NameCheap sandbox user name is: `ApiUser`;
- The value of the API key you have [obtained from NameCheap][nc_api_key]: `ApiKey`;
- The domain for which the aliases will be created: `Domain`.

The config file follow an INI format:

```ini
[Default]
ApiUser=YourNameCheapUserName
ApiKey=aa11bb22cc33dd44ee55ff66aa771234
Domain=example.com
```

Create a `config.ini` or `config-your-domain.ini` file
for each domain you need create/import forwarders for.

Due to a limitation of the API, only one domain can be 
used in a call to created forwarders; a smarter script could
handle multiple domains, but that was beyond my needs
so I have not pursued it. 

Should you have the need to create forwarders in batch 
for multiple domains, you can create multiple
config files and run the script for each one;
alternatively, for a fee 
[I can modify][mailto:philip@variableconsulting.com]
the import file to suit your needs.

### CSV list of aliases

You will need to provide the import script 
with a CSV file where the first column, `Address`, contains
the alias and the second column, `ForwardTo`
contains the destination email.

The alias can be either a simple name, e.g. `contact`
or it can be a full email address, e.g. `contact@example.com`
-- the script strips the domain part.

Here's a sample file:
```
Address,ForwardTo
contact,bob@gmail.com
sales@example.com,jill@outlook.com
press@null.com,ceo@fancy-venture-company.com
```



Assuming you have a CSV file where the first column
contains the alias for a given domain and
the second column contains the destination email,
you can run the following script to import those
aliases into NameCheap and [create forwarders][nc_fwd]
for each row.



## Why?

The Gmail + trick is awesome, but it doesn't work on Google Apps.
If you want email aliases on Google Apps, 
you have to do [add an old-fashion email alias][ga_alias]. 

That has two issues: 

1. It's not easy to do: log out of your account, 
   log in with your admin domain account, 
   add the alias in [5 easy steps][ga_alias],
   log out your admin account,
   and *even then* it might take up to 24 hours;
2. You have a limit of 30 email aliases.

Most people wouldn't probably even care about aliases,
and even fewer people would care about the 30 alias limit.

If you do, because, for example, you want to have one email
address for each important online account in order to reduce 
attack vectors, then the limit is quite easy to reach.

Fortunately, you can do this at least two different ways.

If your shared host provider 

with NameCheap you can set up up to 
[100 forwarding address][nc_fwd]. On the downside, 
you can only do this on separate domain.











[import_script]: 
[ga_alias]: https://support.google.com/a/answer/33327?hl=en
[nc_fwd]: https://www.namecheap.com/support/knowledgebase/article.aspx/308/77/how-to-set-up-free-email-forwarding
[nc_api_key]:
[nc_api_sandbox]:
