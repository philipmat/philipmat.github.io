---
title: Json.NET and NHibernate Serialization Blues
layout: post
snippet: Keep Json.NET from going too deep on NHibernate proxies
---

After spending some irritating hours with Microsoft's [JavaScriptSerializer][jsmvc], 
I've switched over to [Json.NET][json] and I've been happier. That matters. A lot.

I have better control over serialization, for example I can specify how to handle circular references
([ReferenceLoopHandling][serset]), or whether to include nulls ([NullValueHandling][serset]) and/or 
default values ([DefaultValueHandling][serset]); it also gives me more injection points.

Yet it exhibits one frustrating behavior when one of the objects is masked by an NHibernate proxy, 
as it starts to go off the rails and soon the JSON code is riddled with `__interceptors`, and `EventListeners`, 
and various other critters that have no purpose being sent across the wire. 

(Yes, arguably I shouldn't be directly serializing these NHibernate objects, but the DTOs I would use 
would look remarkably similar to the NH objects they would attempt to mock.)

The problem comes with the chaining of strategies a `JsonSerializer` uses to determine how to serialize a particular strategies. 
This chain is captured by the [DefaultContractResolver][dcrc] in the `CreateContract(Type)` method (which thankfully and 
wisely is also `virtual`): it tries in succession to figure out if the type is a primitive, if it's decorated with `Json*Attributes`, 
if it's a dictionary, etc, and eventually it just gives up and creates a plain `JsonObjectContract`.

However, in the middle of that chain is a test for whether the type is `ISerializable`, and unfortunately the NHibernate proxies 
happen to have that attribute, and that is what causes the serializer to go down a rabbit hole.

My solution is to force it to use a `JsonObjectContract` when it encounters one of these proxies.

{% highlight csharp %}
public class IgnoreSerializableJsonContractResolver : DefaultContractResolver
{
    protected override JsonContract CreateContract(System.Type objectType)
    {
        /* Behavior in base we're overriding:
        if (typeof(ISerializable).IsAssignableFrom(objectType))
            return CreateISerializableContract(objectType);
        //*/

        if (objectType.IsAutoClass 
              && objectType.Namespace == null 
              && typeof(ISerializable).IsAssignableFrom(objectType)) {

            return base.CreateObjectContract(objectType);
        }

        return base.CreateContract(objectType);
    }
}


var serializer = new JsonSerializer();
serializer.ContractResolver(new IgnoreSerializableJsonContractResolver());
{% endhighlight %}

I am not sure whether the condition is too restrictive or may generate false positives, but all the NH proxies I've encountered 
seem to exhibit the same behavior: they are auto-generated classes, without a namespace.


[jsmvc]: http://msdn.microsoft.com/en-us/library/system.web.script.serialization.javascriptserializer.aspx
[json]: http://json.codeplex.com/
[jsondoc]: http://james.newtonking.com/projects/json/help/
[serset]: http://james.newtonking.com/projects/json/help/SerializationSettings.html
[dcrc]: http://james.newtonking.com/projects/json/help/html/T_Newtonsoft_Json_Serialization_DefaultContractResolver.htm
