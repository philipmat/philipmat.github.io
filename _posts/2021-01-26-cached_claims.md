---
layout: post
title: Cached Claims when Using Windows Authentication in ASP.NET Core
---

In [Loading Claims when Using Windows Authentication in ASP.NET Core][claims_post]
we examined an approach for injecting [Claims][claims_auth] into the `ClaimsPrincipal`
in order to enable policy usage -- `[Authorization(Policy = "SomePolicy")]` --
on controller actions.

One of the purposes of the `IClaimsTransformation` implementation
is to provide an easier, and somewhat efficient, way to use
authorization policies. As such, we wouldn't be wrong to perform
some expensive operations in the class implementing this interface.
For example, querying a database.

Having than happen on every request is a bit more than annoying
while in development.

While we cannot avoid the calls to the claims transformer,
we can avoid the expensive calls by using a caching approach.  
The title is misleading a bit at this point. We will be caching
the expensive calls and not the claims.

In the [Windows claims example][claims_post], we have
`MagicPowersInfoProvider` as a way to provide information
to the claims transformer, `MyClaimsLoader`, which in turn
determines whether a claim needs to be added to
the `ClaimsIdentity` ([in `TransformAsync`][my_claims]).

`MagicPowersInfoProvider` is registered as a singleton,
which makes is a good place to handle caching.

```csharp
services.AddSingleton<Auth.MagicPowersInfoProvider>();
```

It only makes sense to cache when running under IIS Express.  
Luckily, we don't need to perform any complex detection of
IIS Express. We just need to modify the launchSettings.json
file to add an environment variable:

```json
{
  "profiles": {
    "IIS Express": {
      "commandName": "IISExpress",
      "launchBrowser": true,
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development",
        "CacheClaims": "true"
      }
    },
  ...
```

Then `MagicPowersInfoProvider` can make use of an injected `IMemoryCache`
when the `"CacheClaims"` key is true, which would only be
when running the application from Visual Studio and under IIS Express.

```csharp
public class MagicPowersInfoProvider
{
    private const string CacheClaimsKey = "CacheClaims";
    private const int ClaimCacheInSeconds = 5 * 60;
    private readonly bool _cacheClaims;
    private readonly IMemoryCache _memoryCache;

    public MagicPowersInfoProvider(IConfiguration config, IMemoryCache memoryCache)
    {
        _memoryCache = memoryCache;
        _cacheClaims = config.GetValue<bool>(CacheClaimsKey);
    }

    public async Task<bool> CanHasPowerAsync(string userId)
    {
        if (!_cacheClaims)
        {
            return await ExpensiveHasPowerOperation(userId);
        }

        return await _memoryCache.GetOrCreateAsync<bool>(
            $"power-{userId}",
            async cacheEntry =>
            {
                cacheEntry.SlidingExpiration = TimeSpan.FromSeconds(ClaimCacheInSeconds);
                bool hasPower = await ExpensiveHasPowerOperation(userId);
                return hasPower;
            });
    }

    private Task<bool> ExpensiveHasPowerOperation(string userId)
        => Task.FromResult(true);
}
```

For a full example, containing all the code, see [this repo][repo].

[claims_auth]: https://docs.microsoft.com/en-us/aspnet/core/security/authorization/claims?view=aspnetcore-3.1
[my_claims]: https://github.com/philipmat/AspNetCoreWindowsAuthClaims/blob/master/Auth/MyClaimsLoader.cs#L31
[repo]: https://github.com/philipmat/AspNetCoreWindowsAuthClaims
[claims_post]: /2018/aspnetcore_claims_with_windowsauthentication.html
