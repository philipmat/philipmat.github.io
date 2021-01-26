---
layout: post
title: Loading Claims when Using Windows Authentication in ASP.NET Core 2.x
---

**NOTE 1:** the post below applies to ASP.NET Core 2.x.  
Things have remained conceptually the same in 3.1 and 5.0,
though a few registration options or layouts may have
been changed. For an updated version of the code in here, see
[my Github repo](https://github.com/philipmat/AspNetCoreWindowsAuthClaims)
which contains a fully runnable sample.

**NOTE 2:** When using IIS Express, the claim transformation
mentioned in this post is called on each request.  
The [Cached Claims post](/2021/cached_claims.html)
suggests an approach to overcoming this behavior.

Much like almost everything else in ASP.NET Core,
[enabling Windows Authentication in ASP.NET Core][configure_winauth]
is well documented and has superb step-by-step examples.

The [Claims-based authorization system][claims_auth] is documented
just as well and the examples are well chosen.

Where I thought the documentation fell short was the marrying
of the two concepts; there is little explanation given
to how the claims are actually made available to be
check and asserted on.

If we were to inspect the `Identity` of a `User`,
we would notice that it already has a substantial
`Claims` collection. These claims are all seemingly
associate with specific Windows user properties,
and to me have largely legible names yet indecipherable
values, save perhaps for the `.../name` claim:

| Type | Value |
|------|-------|
| <http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name> | HOME\philip|
| <http://schemas.microsoft.com/ws/2008/06/identity/claims/primarysid> | S-1-5-21-616010284-1202357983-1921873989-1000 |
| <http://schemas.microsoft.com/ws/2008/06/identity/claims/groupsid> | S-1-1-0 |
| <http://schemas.microsoft.com/ws/2008/06/identity/claims/groupsid> | S-1-5-4 |
| etc | etc |

In contrast, the [Claims examples][claims_auth] make use of such
nicely named claims like `"EmployeeNumber"` or `ClaimTypes.DateOfBirth`,
none of which can be found in the claims collection of our Windows user.

To load claim in ASP.NET Core 2.x we make use of one or more
*claims transformations*, classes implementing
[`IClaimsTransformation`][iclaimstransf]
(used to be called `IClaimsTransformer` in earlier versions),
which get access to the `ClaimsPrincipal` and can
construct new ones or add claims to the loaded one.

In the following example we'll look at adding our own claims to
the collection. To make it a bit more interesting, let's assume
we have a table in the database that stores the ids of the users
who are administrators of our own application and we would
like to add a flag in claims if a user logging in is part of this table.

Assuming we use these in combination with `Authorize` attribute,
likely to check for an `"IsAdmin"` claim: `[Authorize(Policy = "IsAdmin")]`,
we will be making the following changes to our application:

## Packages required

If running against .NET Core 2.x, the `Microsoft.AspNetCore.App` meta-package is sufficient.

If running against .NET Framework 4.6+, we need to add:

* `Microsoft.AspNetCore.Authentication` - provides a large host
  of authorization classes, policies, and convenience extension methods;
* `Microsoft.AspNetCore.Server.IISIntegration` - adds support for IIS (and IIS Express)
  in further support of the authentication process.

## Code changes

### launchSettings.json

Enable Windows authentication for IIS. Also enable anonymous access
if usage of `[AllowAnonymous]` attribute is needed:

```JSON
{
  "iisSettings": {
    "windowsAuthentication": true,
    "anonymousAuthentication": true,
...
```

### Startup.cs

Enable authentication by adding the following to the
`Configure(IApplicationBuilder app, ...)` method:

```csharp
app.UseAuthentication();
```

Add IIS authentication scheme in `ConfigureServices`:

```csharp
services.AddAuthentication(IISDefaults.AuthenticationScheme);
```

We'll be back here in a bit to register our claims loader

### ClaimsLoader.cs

Before we implement `IClaimsTransformation` a couple notes about it.

First, they run on each `AuthenticateAsync` call, which means
for IIS Authentication they run only once and whatever claims
we add to the collection are cached for as long as the user
is logged in.  
If we remove a logged in user from the list of administrators,
they will continue to behave as such until they log in again.

Second, they run *on each* `AuthenticateAsync` call, so we will
heed this warning from the
[documentation of `TransformAsync`][transfasync]:

> Note: this will be run on each AuthenticateAsync call,
so its safer to return a new ClaimsPrincipal if your transformation is not idempotent.

This is because if any call (tests?) causes `AuthenticateAsync`
to be called twice, the same claim is added twice to the collection
as pointed out in [this article by Brock Allen][ba_claims_multiple].

```csharp
using System.Security.Claims; // for ClaimsPrincipal
using Microsoft.AspNetCore.Authentication; // for IClaimsTransformation

public class ClaimsLoader : IClaimsTransformation
{
    public const string IsAdminKey = "IsAdmin";
    private readonly UserContext _userContext;

    public MigrationsUserClaimsLoader(UserContext userContext)
    {
        _userContext = userContext;
    }

    public async Task<ClaimsPrincipal> TransformAsync(ClaimsPrincipal principal)
    {
        var identity = (ClaimsIdentity)principal.Identity;

        // create a new ClaimsIdentity copying the existing one
        var claimsIdentity = new ClaimsIdentity(
            identity.Claims,
            identity.AuthenticationType,
            identity.NameClaimType,
            identity.RoleClaimType);

        // check if our user is in the admin table
        // identity.Name is the domain-prefixed id, eg HOME\philip
        if (await _userContext.IsAdminAsync(identity.Name))
        {
            claimsIdentity.AddClaim(
                new Claim(IsAdminKey, "So say we all"));
        }

        // create a new ClaimsPrincipal in observation
        // of the documentation note
        return new ClaimsPrincipal(claimsIdentity);
    }
}
```

### Startup.cs - adding policy

Now that we created our claims loader, let's register it with the
service collection and add a policy for it too:

```csharp
services.AddTransient<IClaimsTransformation, ClaimsLoader>();

services.AddAuthorization(options =>
{
    options.AddPolicy(
        "IsAdmin",
        policy => policy.RequireClaim(ClaimsLoader.IsAdminKey));
});
```

At this point we can decorate our controllers or controller
actions and employ the policy we just added:

```csharp
[Authorize(Policy = "IsAdmin")]
public Task<IActionResult> AddUser() {
    ...
}
```

## Variation

The example adds the `"IsAdmin"` claim only if the user is an admin.

If we wanted to add the claim anyway and rely on the value of the claim,
the code changes as following:

### ClaimsLoader.cs - variation

```csharp
bool isAdmin = await _userContext.IsAdminAsync(identity.Name));
claimsIdentity.AddClaim(new Claim(IsAdminKey, isAdmin ? "yes" : "no"));
```

### Startup.cs - variation

```csharp
services.AddAuthorization(options =>
{
    options.AddPolicy(
        "IsAdmin",
        policy => policy.RequireClaim(ClaimsLoader.IsAdminKey, "yes"));
});
```

or to add a JavaScript flavor to it ;)

```csharp
services.AddAuthorization(options =>
{
    options.AddPolicy(
        "IsAdmin",
        policy => policy.RequireClaim(
            ClaimsLoader.IsAdminKey,
            "yes", "Yes", "true", "True", "1")); // ugh
});
```

[configure_winauth]: https://docs.microsoft.com/en-us/aspnet/core/security/authentication/windowsauth?view=aspnetcore-2.1
[claims_auth]: https://docs.microsoft.com/en-us/aspnet/core/security/authorization/claims?view=aspnetcore-2.1
[ba_claims_multiple]: https://brockallen.com/2017/08/30/beware-in-asp-net-core-2-0-claims-transformation-might-run-multiple-times/
[transfasync]: https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.authentication.iclaimstransformation.transformasync?view=aspnetcore-2.1#Microsoft_AspNetCore_Authentication_IClaimsTransformation_TransformAsync_System_Security_Claims_ClaimsPrincipal_
[iclaimstransf]: https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.authentication.iclaimstransformation?view=aspnetcore-2.1
