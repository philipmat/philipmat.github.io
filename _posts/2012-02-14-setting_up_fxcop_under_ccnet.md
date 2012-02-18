---
title: Setting up FxCop under CruiseControl.NET
layout: post
---

After spending up half a day trying to get [FxCop][fxcop] v1.36 to play nice with [CruiseControl.NET][ccnet] and MSBuild, 
I thought it was worth spending an extra hour or two documenting it.

There are two ways we can get FxCop running under CCNet: the easy way and (what I think it's) the right way. 

Either way, we start by creating an FxCop project using the FxCop GUI; it makes it easy to add our assemblies 
and to select the rules we'd like enforced.

**The easy way** has us using an `<Exec/>` task within the MSBuild file:

{% highlight xml %}
<Target Name="FxCop" DependsOnTargets="Build;RunFastTests">
  <Delete Files="$(ProjectRoot)\fxcop.xml" />
  <Exec Command="&quot;$(FxCopPath)\FxCopCmd.exe&quot;
    /dic:&quot;$(ProjectRoot)\src\CodeNameDictionary.xml&quot;
    /project:$(ProjectRoot)\src\Default.FxCop /out:$(ProjectRoot)\fxcop.xml" 
    ContinueOnError="true">
  </Exec>
</Target>
{% endhighlight %}

In this version, we're telling FxCop command line tool to use a custom dictionary - more on this later,
the project file we created earlier, and to output the results to an XML file. 

When being run, FxCop tends to load the previous results, which would cause load errors if we renamed classes that previously had errors,
so we'll `<Delete/>` the output file before running the task.


<p>&nbsp;</p>

**The nicer, more explicit way**, has us use the supplemental tasks provided by the [MSBuild Community Tasks Project][mct],
in particular the `<FxCop/>` task (grab at least version 1.3.0.528, part of the *nightly builds* - v1.2 doesn't 
properly support this task).

{% highlight xml %}
<Target Name="FxCop" DependsOnTargets="Build;RunFastTests">
  <Delete Files="$(ProjectRoot)\fxcop.xml" />
  <FxCop
    ToolPath="$(FxCopPath)\FxCopCmd.exe"
    ProjectFile="$(ProjectRoot)\src\Default.FxCop"
    CustomDictionary="$(ProjectRoot)\src\CodeNameDictionary.xml"
    FailOnError="false"
    AnalysisReportFileName="$(ProjectRoot)\fxcop.xml"
  />
</Target>
{% endhighlight %}

What you won't find in the MSBuild Community Tasks documentation is the requirement to use the `ToolPath` to point to the right version 
of FxCop. As of now, the `<FxCop/>` task looks explicitly for FxCop v1.32 and for a registry key that no longer exists 
when it tries to build the full command line:

{% highlight csharp %}
...
if (string.IsNullOrEmpty(ToolPath)) {
  string fxCopPath = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
  fxCopPath = Path.Combine(fxCopPath, @"Microsoft FxCop 1.32");
  try {
    using (RegistryKey buildKey = Registry.ClassesRoot.OpenSubKey(@"FxCopProject\shell\Open\command")) {
      if (buildKey == null) {
        Log.LogError("Could not find the FxCopProject File command in the registry. Please make sure FxCop is installed.");
      } else {
        fxCopPath = buildKey.GetValue(null, fxCopPath).ToString();
        ...
{% endhighlight %}

The problem with the registry look up is that FxCop v1.36 uses a key called `FxCop.Project.9.0`,
all which means that the `<FxCop/>` task fails to find the executable. That is why we have to use the 
`ToolPath`, inherited from its `Task` parent, to help it find it.

Alright, now the promised dictionary clarification.

If our namespaces, classes, etc. include non-lexical words, for example `Flickr.Configurator`, FxCop will announce  
that our code breaks a naming rule - `CA1704:IdentifiersShouldBeSpelledCorrectly` - and will tell us to:

> Correct the spelling of 'Flickr' in assembly ExternalDependencies.dll'.
>
> Correct the spelling of 'Configurator' in assembly ExternalDependencies.dll'.

(Yes, *Configurator* is not an English word either - us developers have a lot of those.)

We'll fix this problem by adding a [custom FxCop dictionary][dict] containing the words we want to mark as correct:

{% highlight xml %}
<Dictionary>
  <Words>
    <Recognized>
      <Word>Flickr</Word>
      <Word>Configurator</Word>
    </Recognized>
  </Words>
</Dictionary>
{% endhighlight %}

We'll then spell  this dictionary using the `CustomDictionary` property of the `<FxCop/>` task. 


We could and should also add the dictionary into the FxCop project file to make sure the GUI doesn't complain
about those naming rules being broken either. Find the `<CustomDictionaries/>` node within the project file,
`Default.FxCop` in the examples above, and add a `<CustomDictionary/>` node:

{% highlight xml %}
<CustomDictionaries SearchFxCopDir="True" SearchUserProfile="True" SearchProjectDir="True">
  <!-- Tells FxCop to find it in the same location as the Default.FxCop file -->
  <CustomDictionary Path="CodeAnalysisDictionary.xml" />
</CustomDictionaries>
{% endhighlight %}


<p>&nbsp;</p> 

CCNet captures all the output of a build into a giant result file using `<merge>` tasks.
We'll follow the [instructions on the CCNet website][ccnet_fxcop] to merge in the generated `fxcop.xml` file:

{% highlight xml %}
<tasks>
  <merge>
    <files>
      <file>fxcop.xml</file>
      <!-- Other files to merge for your build would also be included here -->
  	</files>
  </merge>
</tasks>
{% endhighlight %}

Finally, to be able view the results of the FxCop analysis in CCNet's web dashboard, we'll need to include 
the XSLT files, which extract and pretty up the entries merged in from `fxcop.xml`, into 
the `dashboard.config` file, typically located within `C:\Program Files\CruiseControl.NET\webdashboard\` folder:

{% highlight xml %}
...
<buildPlugins>
  <buildReportBuildPlugin>
    <xslFileNames>
      <!-- other xsl file, such nunit and msbuild -->
	  <xslFile>xsl\fxcop-summary_1_36.xsl</xslFile>
	  <xslFile>xsl\fxcop-report_1_36.xsl</xslFile>
    </xslFileNames>
  </buildReportBuildPlugin>
  <buildLogBuildPlugin />
  <!-- These create two menu entries on the left, when viewing a project's build page -->
  <xslReportBuildPlugin description="FxCop Summary" actionName="FxCopSummary" xslFileName="xsl\fxcop-summary_1_36.xsl"></xslReportBuildPlugin>
  <xslReportBuildPlugin description="FxCop Report" actionName="FxCopReport" xslFileName="xsl\fxcop-report_1_36.xsl"></xslReportBuildPlugin>
</buildPlugins>
{% endhighlight %}


That's it. Next time you build you should see the FxCop details when you click the "FxCop Report" link.

The only one thing to note is that violating FxCop rules, no matter their level or the value of `ContinueOnError`,
will not mark the build a broken. If you want FxCop failures to break the build, there is 
[one further step](http://sharpfellows.com/post/Getting-FxCop-to-break-the-build.aspx) you need to take.
 

[fxcop]: http://msdn.microsoft.com/en-us/library/bb429476(v=vs.80).aspx
[ccnet]: http://www.cruisecontrolnet.org/
[ccnet_fxcop]: http://confluence.public.thoughtworks.org/display/CCNET/Using+CruiseControl.NET+with+FxCop
[mct]: http://msbuildtasks.tigris.org/
[dict]: http://msdn.microsoft.com/en-us/library/bb429472(v=vs.80).aspx
