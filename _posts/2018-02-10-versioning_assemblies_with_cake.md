---
layout: post
title: Versioning Assemblies with Cake and Git
---

## Requirements

1. Given an application, I want to be able to **trace its binaries**
 back to the source code "version" it was built from;
2. As such, I want this identification ability to be **automatically employed**
  during the build process;
3. I want to have **easy ways of retrieving this information**,
  as well as the **version of code** it was built from;
4. All files built at the **same time** have the **same version**;
5. I use **git** for VCS and **Cake** for build scripts;
6. I don't want **trivial commits**,
  such as those containing only the identifying information.

## Proposed solution

* Employ a way of versioning (duh) that is tied to individual files;  
  Satisfies requirement 1;
* Include the git branch information;
* Include the commit id (SHA1) of the `HEAD` as a way of identifying the exact state of the code;  
  Satisfies requirements 2 and 5;
* Only built from committed code (no uncommitted files);  
  Satisfies requirements 2, 3, and 4;
* If files are modified for versioning purposes,
  roll back the changes at the end of the build, even if the build had errors;  
  Satisfies requirement 6.

### Technical Details

As far as the versioning goes, there are several version numbers associated with a .Net assembly:

* _Assembly version_, important to the .Net loader - set with [`AssemblyVersion` attribute][avattr]:
  usually in `Properties/AssemblyInfo.cs`.  
  Must be in *major.minor.build.version* format, all numbers, or the compiler
  throw a `CS7034` error:
  > error CS7034: The specified version string does not conform to the required format - major[.minor[.build[.revision]]]
* _File version_, a property of the file itself and inspect-able in the *Details*
  section of the file properties dialog is set using the [`AssemblyFileVersion` attribute][fileverattr].  
  There's a warning, but not an error
  (unless we have `\<TreatErrorsAsWarnings>true\</TreatErrorsAsWarnings>`, which we should),
  if we don't follow the same format as the assembly version:
  > warning CS7035: The specified version string does not conform to the recommended format - major.minor.build.revision
* _Product version_ is another property of visible in the file properties dialog,
  is set using the [`AssemblyInformationalVersion` attribute][infoverattr],
  and is the most permissible of the three as it literally accepts any string,
  although we should set it to something reasonable and meaningful to
  whomever inspects it.
  ![Product Version with Emoji](/media/images/product_info.png)

This [Stack Overflow answer](https://stackoverflow.com/a/65062),
and the ones that follow,
provides really good descriptions of each attribute, its limitations,
and intended use.

Because we want to include the branch name and the commit id (SHA1),
the `AssemblyInformationalVersion` is the only we can use.

We propose the following format: `Major.minor.branch-sha1`.

The assembly version can be dynamically versioned by MSBuild using
the format `[assembly: AssemblyVersion("1.0.*")]` as a way of providing
supplemental information about the date and time of build -
see the [Remarks section of the AssemblyVersion docs][avattrremarks].

## Implementation

We'll make use of the [Cake.Git][cakegit] add-in and Cake's ability
to generate the assembly information using `CreateAssemblyInfo` method.

To simplify matters, we'll split `AssemblyInformationalVersion` attribute
from the `Properties/AssemblyInfo.cs` file into its own
`Properties/AssemblyInfoVersion.cs`. Its content is unimportant,
but we'll start with a value of:

```csharp
[assembly: System.Reflection.AssemblyInformationalVersion("1.0.0.")]
```

Next we'll create a `Task("Version")` in our `build.cake` file that
creates the `AssemblyInfoVersion.cs` file, we'll make the *Build*
task depend upon it, and we'll revert the changes at the end of
the build process.

```csharp
#addin nuget:?package=Cake.Git

var configuration = Argument("configuration", "Debug");
var thisRepo = MakeAbsolute(Directory("./"));
var assemblyInfo = File("./TestAssemblyVersioning/Properties/AssemblyInfoVersion.cs");

Task("Version")
    .Does(() => 
{
    var branch = GitBranchCurrent(thisRepo);

    // The following is not the best approach
    // We should use LibGit2Sharp's ObjectDatabase.ShortenObjectId(),
    // but Cake.Git doesn't currently support it.
    var sha = branch.Tip.Sha.Substring(0, 8);

    CreateAssemblyInfo(assemblyInfo, new AssemblyInfoSettings {
        InformationalVersion = string.Format("1.0.{0}-{1}", branch.FriendlyName, sha)
    });
});

Task("Build")
    .IsDependentOn("Version")
    .IsDependentOn("Restore-NuGet-Packages")
    .Does(() =>
{
    if(IsRunningOnWindows())
    {
      MSBuild(sln, settings => settings.SetConfiguration(configuration));
    }
    else
    {
      XBuild(sln, settings => settings.SetConfiguration(configuration));
    }
})
.Finally(() =>
{
    // restore assembly.cs files
    GitCheckout(thisRepo, new FilePath[] { assemblyInfo });
});
```

That's it. Now every time we build the project using our build script,
the product version will reflect it accordingly:

![Product Version with Git Info](/media/images/product_info2.png)

*Note*: if we had multiple assemblies, like normal projects do,
we would have a single `AssemblyInfoVersion.cs`, likely in the root of the project,
and we would link that file into each project to ensure they all get
the same product version:

```xml
<Compile Include="..\AssemblyInfoVersion.cs">
    <Link>Properties\AssemblyInfoVersion.cs</Link>
</None>
```




[avattr]: https://msdn.microsoft.com/en-us/library/system.reflection.assemblyversionattribute(v=vs.110).aspx
[avattrremarks]: https://msdn.microsoft.com/en-us/library/system.reflection.assemblyversionattribute(v=vs.110).aspx#Remarks
[fileverattr]: https://msdn.microsoft.com/en-us/library/system.reflection.assemblyfileversionattribute(v=vs.110).aspx
[infoverattr]: https://msdn.microsoft.com/en-us/library/system.reflection.assemblyinformationalversionattribute(v=vs.110).aspx 
[cakegit]: https://cakebuild.net/dsl/git/