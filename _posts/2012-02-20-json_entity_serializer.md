---
title: JSON Entity Converter
layout: post
---

Whether in the context of my friend Curtis's [BORAX][borax] proposal, or [my own][webmvc],
we will eventually need to serialize our domain objects and ship them to the browser.

Our best solutions is probably some sort of [Domain Transfer Object (DTO)][dto], 
but for a second let's assume we take the quick route and turn our domain objects 
directly into JSON mush.

Is ASP.NET MVC 3 we can use the [JsonResult][json_result] class, but with it comes a problem: 
the [JavaScriptSerializer][jsser], which `JsonResult` uses, 
cannot handle circular references (and rightfully so since JSON doesn't have references).

Let me illustrate using the following simplified domain classes (you can find the full code in [this Gist][gh]):

{% highlight csharp %}
public class Entity {  // Layer Supertype
    public int Id { get; set; }
}

public class Company : Entity { 
    public string Name { get; set; }
    public Contact MainContact { get; set; }
}

public class Contact : Entity {
    public string Name { get; set; }
    public Company WorksFor { get; set; }
}
{% endhighlight %}

When serializing an object of type `Company`, the `JavaScriptSerializer` will choke on `Contact.WorksFor` 
since it points back to the `Company` that the contact is associated with.

Before we talk about how we'll fix it, let's talk about the output.
What I think I'd like to have when serialize a company to JSON is: 

{% highlight js %}
{
    "Id" : 1,
    "Name" : "Moof",
    "MainContact" : {
        "Id" : 100,
        "Name" : "Clarus",
        "WorksFor" : {
            "TypeName" : "Company",
            "Id" : 1
        }
    }
}
{% endhighlight %}

In other words, if one of the object we try to serialize has 
a property of type `Entity`, we'll just output its `Id` and assume the consumer of the JSON will 
know to request `/refdata/{entitytypes}/{id}` to resolve it, if needed.

Of course, this will not avoid circular references entirely, but merely provide an example 
on how to work with the class that will solve our particular problem: [JavaScriptConverter][jsconv].

`JavaScriptConverter`, of the `System.Web.Script.Serialization` clan, allows us to inject specific 
type handlers into `JavaScriptSerializer` and 
have it defer to our converter when encountering those types in the serialization process. 
And it gets better: our converter won't have to provide *actual JSON*, it merely has to 
return a dictionary of name-value pairs and the `JavaScriptSerializer` will take care 
of the actual transformation.

Here's how we could implement the required `Serialize` method:

{% highlight csharp %}
public override IDictionary<string, object> Serialize(object obj, JavaScriptSerializer serializer) {
    var ret = new Dictionary<string, object>();
    string name; object value;
    
    var props = obj.GetType().GetProperties(BindingFlags.Instance | BindingFlags.Public | BindingFlags.GetProperty);
    foreach (PropertyInfo prop in props) {
        name = prop.Name;
        value = prop.GetValue(obj, null);
        if (value != null && typeof(Entity).IsAssignableFrom(prop.PropertyType))
            // real gist code: ret.Add(name, _reducer((Entity) value)); //
            ret.Add(name, new Dictionary<string, object> { 
                { "TypeName", value.GetType().name },
                { "Id", ((Entity) value).Id }
            });
        else
            ret.Add(name, value);
    }
    
    return ret;
}
{% endhighlight %}

(Of course the [actual implementation][gh] is a bit more elegant, I hope)

We can now serialize objects such as these:

{% highlight csharp %}
var co = new Company { Id = 1, Name = "Moof Inc." };
var clarus = new Contact { Id = 1, Name = "Clarus" };
var mark = new Contact { Id = 2, Name = "Mark" };
co.AddContact(clarus);
co.AddContact(mark);
co.MainContact = clarus;

var converter = new EntityConverter(new[] { typeof(Contact) });
var serializer = new JavaScriptSerializer();
serializer.RegisterConverters(new[] { converter });
serializer.Serialize(co).Dump(); 

{% endhighlight %}

And get the following JSON representation: 

{% highlight js %}
{
    "Id": 1, 
    "Name": "Moof Inc.",
    "Contacts": [
        {
            "Id": 1, 
            "Name": "Clarus", 
            "WorksFor": {
                "Id": 1, 
                "TypeName": "Company"
            }
        }, 
        {
            "Id": 2, 
            "Name": "Mark", 
            "WorksFor": {
                "Id": 1, 
                "TypeName": "Company"
            }
        }
    ], 
    "MainContact": {
        "Id": 1, 
        "Name": "Clarus", 
        "WorksFor": {
            "Id": 1, 
            "TypeName": "Company"
        }
    } 
}
{% endhighlight %}

The [full code][gh] - designed to work with the most excellect [LINQPad][linqpad], 
shows three attempts (four if we include the failed circular reference error) 
and with them the various ways the `EntityConverter` can control the JSON output.

If you want to use the code in Visual Studio, add a reference to `System.Web.Extensions` 
and import the `System.Web.Script.Serialization` namespace.




[gh]: https://gist.github.com/1868672
[borax]: http://curtis.schlak.com/2012/01/24/borax.html
[webmvc]: http://philipm.at/2012/0121/
[supertype]: http://martinfowler.com/eaaCatalog/layerSupertype.html
[curtis_dto]: http://curtis.schlak.com/2012/01/26/dto-aint-an-o.html
[dto]: http://martinfowler.com/eaaCatalog/dataTransferObject.html
[json_result]: http://msdn.microsoft.com/en-us/library/system.web.mvc.jsonresult(v=vs.100).aspx
[jsser]: http://msdn.microsoft.com/en-us/library/system.web.script.serialization.javascriptserializer.aspx
[jsconv]: http://msdn.microsoft.com/en-us/library/system.web.script.serialization.javascriptconverter.aspx
[linqpad]: http://www.linqpad.net/ 
