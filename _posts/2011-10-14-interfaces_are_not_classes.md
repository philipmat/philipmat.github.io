---
title: .Net Interfaces Are Not Classes 
snippet: A brief look at .Net instance and class inheritance through the lens of DataBinding.
layout: post
has_tldr: yes
---


Well, duh! Right?

To be honest, if you know that already, and who doesn't, then this post does not have much to offer, except a tale of `DataBinding` exceptions, `TypeConverters`, and a few interesting tid-bits I picked up along the way, along with what I think it's a bug in a core .Net class.

Throughout this post I will use two interface and two classes implementing them to make my point:

```csharp
interface IBase {
  string BaseMethod();
}
interface IDerived : IBase {
  string DerivedMethod();
}

class Base: IBase {
  public string BaseMethod() { return "BaseMethod"; }
}
class Derived : Base, IDerived {
  public string DerivedMethod() { return "DerivedMethod"; }
}
```

Rocket surgery, innit?

<a name="databinding_and_interfaces"> </a>

## data binding and interfaces

Good OOP (Object Oriented Programming) code monkeys have designed and programmed against abstractions, e.g., *interfaces*, before Uncle Bob articulated the [SOLID principles](http://blog.objectmentor.com/articles/2009/02/12/getting-a-solid-start), and I like to believe that even before the advent of the [Dependency Inversion principle](http://en.wikipedia.org/wiki/Dependency_inversion_principle).

It only makes sense that we apply the same principle, programming against interfaces, to [MVVM (Model View ViewModel)](http://en.wikipedia.org/wiki/MVVM) design, as it shows in this overly simplistic example:

```csharp
class MyForm : Form {
  public IBase Base { get; set; }
  public IDerived Derived { get ; set; }

  protected override void OnLoad(EventArgs e) {
    this.Text += ":" + (Base == null 
                          ? "Base is null" 
                          : Base.BaseMethod());
    this.Text += ":" + (Derived == null 
                          ? "Derived is null" 
                          : Derived.DerivedMethod());
  }
}
class MyViewModel  {
  public IBase Base { get { return new Base(); } }
  public IDerived Derived { get { return new Derived(); } }
}
```

I'm using `Windows.Forms` because WPF would've been too verbose for such a tiny task, but the concept translates almost word for word.

MVVM was designed to make use of binding, `DataBinding` to be more specific:

```csharp
void Main()
{
  MyForm viewBase = new MyForm { Text = "Base" }, 
         viewDerived = new MyForm { Text = "Derived" };
  var viewModel = new MyViewModel();

  viewBase.DataBindings.Add("Base", viewModel, "Base", 
                            false, 
                            DataSourceUpdateMode.OnPropertyChanged);
  viewDerived.DataBindings.Add("Derived", viewModel, "Derived", 
                               false, 
                               DataSourceUpdateMode.OnPropertyChanged);

  viewBase.Show();
  viewDerived.Show();
}
```

Running that code ([here is the script](/media/files/databinding.linq) to use with [LINQPad](http://www.linqpad.net/)) we'd expect to get two windows with titles "Base:BaseMethod", and respectively "Derived:DerivedMethod", yet instead we get two big, fat, `FormatExceptions` that make as much sense as a fish with a bicycle (full stack trace [here](https://gist.github.com/1283578#file_gistfile1.txt) and also notice how early in the control's lifecyle this error happens):

```
System.FormatException: Cannot format the value to the desired type.
   at System.Windows.Forms.Binding.FormatObject(Object value)
   ...
   at System.Windows.Forms.Control.UpdateBindings()
   ...
   at System.Windows.Forms.Control.CreateControl()
   at System.Windows.Forms.Control.WmShowWindow(Message& m)
   at System.Windows.Forms.Control.WndProc(Message& m)
   at System.Windows.Forms.ScrollableControl.WndProc(Message& m)
   at System.Windows.Forms.Form.WmShowWindow(Message& m)
   at System.Windows.Forms.Form.WndProc(Message& m)
   at System.Windows.Forms.Control.ControlNativeWindow.OnMessage(Message& m)
   at System.Windows.Forms.Control.ControlNativeWindow.WndProc(Message& m)
   at System.Windows.Forms.NativeWindow.Callback(IntPtr hWnd, Int32 msg, IntPtr wparam, IntPtr lparam)
```

Cannot _format_ ?! And format what - a `Base` into an `IBase`? How is that possible?



## the devil is in the code

Very puzzled, I pulled out a decompiler, [JetBrains' dotPeek](http://www.jetbrains.com/decompiler/), took a look at `Binding.FormatObject(Object)`, and found these interesting lines:

```csharp
//-  propertyType is typeof(IBase)
//-  value is our new Base()
//-  so is obj1
if (propertyType == typeof (object))
  return value;
if (obj1 != null && 
    (obj1.GetType().IsSubclassOf(propertyType) || 
     obj1.GetType() == propertyType))
  return obj1;
```

I'm pretty sure this would've jumped out at you, dear reader, because you're so much smarter, but in my head it didn't make any sense; I thought "of course `Base` is a child of `IBase` - what's your problem?".

Yes, `Base` is a _child_ of `IBase`, for very fuzzy values of _child_, but it is not a _subclass_ of `IBase`: `Base` _implements_ `IBase` but does not _inherit_ from `IBase`.

Given the direction of the assignment, I believe this is a bug: `IsSubclassOf` is an unnecessary restriction, they should have used `propertyType.IsAssignableFrom(obj1.GetType())` instead, which would've taken care of this mess and allow for binding onto an interface to happen as expected.

Well, let's debate that later, how do we fix it?

Obviously we could change `MyForm.Base` to be of type `Base` and `MyForm.Derived` to be of either type `Derived` or `Base`. That would work, and it's a reasonable fix if you happen to dislike abstractions.

You could also change both properties to be of type `object`, but that just means you have OOP in general.

The next few instructions in `Binding.FormatObject` contain another solution:

```csharp
TypeConverter converter = 
    TypeDescriptor.GetConverter(value != null 
                                ? value.GetType() 
                                : typeof (object));
if (converter != null && converter.CanConvertTo(propertyType))
  return converter.ConvertTo(value, propertyType);
```

You can [read more](http://msdn.microsoft.com/en-us/library/system.componentmodel.typeconverter.aspx) about the `TypeConverter`, while I create one for the `Derived` class and then decorate it using the `TypeConverterAttribute`:

```csharp
class DerivedConverter : TypeConverter {
  private readonly Type typeD = typeof(Derived);
  public override bool CanConvertTo(ITypeDescriptorContext context, Type destinationType) {
    if (destinationType.IsAssignableFrom(typeD)) 
      return true;
    return base.CanConvertFrom(context, destinationType);
   }
   
  public override object ConvertTo(ITypeDescriptorContext context, CultureInfo culture, 
         object value, Type destinationType) {  
    if (destinationType.IsAssignableFrom(typeD)) 
      return value;
    return base.ConvertTo(context, culture, value, destinationType);
  }
}

[TypeConverter(typeof(DerivedConverter))]
class Derived : Base, IDerived {
  public string DerivedMethod(){return "DerivedMethod"; }
}

```

If you rerun the script with the `TypeConverter` in place, you'll only get one exception for `IBase`, while the `IDerived` example performs as expected.

Kind of silly, isn't it, to use a separate class to convert an instance into the interface it implements anyway.

It was at this point that I did what any sane developer would do when faced with this snafu: bitch on Twitter. Rory Primrose ([@roryprimrose](https://twitter.com/roryprimrose) - you should follow him replied) with an example of his own, this one around interface inheritance.


<a name="inheritance"> </a>

## interface inheritance

[His assumption](http://www.neovolve.com/post/2008/07/03/reflection-pop-quiz-does-interface-inheritance-exist.aspx) was that calling `Type.GetMethods` on a derived interface would also return the methods of its parent(s).

I had to try and cook some of [my own code](/media/files/interfaces_are_not_classes.linq) and here are the surprising results:

```csharp
BindingFlags 
  inst_pub = BindingFlags.Instance | BindingFlags.Public,
  flat_inst_pub = BindingFlags.FlattenHierarchy | inst_pub,
  decl_inst_pub = BindingFlags.DeclaredOnly | inst_pub;
Action<string, Array> logm = (s, a) => a.Length.Dump(s);

Derived d = new Derived();
Type iB = typeof(IBase),
iD = typeof(IDerived),
cB = typeof(Base),
cD = d.GetType();

logm("Instance | Public", cD.GetMethods(inst_pub));                   //=> 6
logm("Flatten | Instance | Public", cD.GetMethods(flat_inst_pub));    //=> 6
logm("Declared | Instance | Public", cD.GetMethods(decl_inst_pub));   //=> 1

logm("Instance | Public", iD.GetMethods(inst_pub));                   //=> 1
logm("Flatten | Instance | Public", iD.GetMethods(flat_inst_pub));    //=> 1?!

cD.IsSubclassOf(cB).Dump("Derived subclass of Base?");                //=> True
(d is Base).Dump("Derived is Base");                                  //=> True
cD.IsSubclassOf(iD).Dump("Derived subclass of IDerived?");            //=> False
(d is IDerived).Dump("Derived is IDerived");                          //=> True

iD.IsAssignableFrom(cD).Dump("Derived assignable to IDerived?");       //=> True
iD.IsSubclassOf(iB).Dump("IDerived subclass of IBase?");               //=> False?!
iB.IsAssignableFrom(iD).Dump("IDerived assignable IBase?");            //=> True
```

The classes behave as expected (2 methods + 4 from `Object`), but I expected `FlattenHierarchy` with `IDerived` to return two methods: its own `DerivedMethod` and its parent `BaseMethod`.  

Probing further, shows not only that *classes are not subclasses of the interfaces they implement, but neither are interfaces subclasses of their parents*.

Much sooner that I, Rory asked the question at the core of his post: 

> Does interface inheritance exist?

Much to my amazement, the answer is no, at least according to reflection. This is completely not what I had assumed.

<a name="when_in_doubt"> </a>

## when in doubt

... look up the specs.

In highsight, it should all have been obvious. My mistake lies in thinking of interfaces as purely virtual/abstract classes (there's some C++ roots showing - only pointing that out to get some street cred). 

However, that shows fault immediately because, even if it was so - even if interfaces were purely virtual _classes_, *the CLI does not support multiple class inheritance* (but you knew that already, didn't you), yet it supports multiple interface inheritance using the exact same syntax.

The standard, "ECMA-335":ecma355, explicitly states in _8.9.9 Object type inheritance_ that:

> [...] all object types shall either explicitly or implicitly declare support for (i.e., inherit from) exactly one other object type.


If I were to nitpick though, I would point out that the C# standard, "ECMA-334":ecma334, is a bit inconsistent in usage: within _8.9 Interfaces_ you will read "Interfaces can employ multiple inheritance", which is contradicted by _ECMA-335 8.10 Member inheritance_:

> While interface types can be derived from other interface types, they only “inherit” the requirement to implement method contracts, never fields or method implementations. 

This is a CLI restriction: while ordinary C++ does support multiple inheritance, Managed C++ doesn't.  [This blog post](http://blogs.msdn.com/b/slippman/archive/2004/08/05/209606.aspx) shares Managed C++ team's decision and includes this grain of insight about Eiffel's support of multiple inheritance on the CLI:

> [...] the CLI does not, for example, support private inheritance, value inheritance (that is, the inheritance of implementation but not of type), or multiple inheritance (MI). While a language can choose to support these aspects of inheritance, that support requires a mapping onto the existing CLI object model because there is no direct support.

The Eiffel language under CLI, for example, choose to provide an MI mapping.


<a name="tldr"> </a>

## conclusion

What did we learn?

In truth, there's no true inheritance in the CLI when it comes to interfaces - that is reserved for classes; in practice, we can consider interface inheritance exists as long as we use those relationships for typing rather than reflection.

If you perform runtime type inspection with a goal to see if casting is possible, use `Type.IsAssignableFrom`, rather than `Type.IsSubclassOf`. I cannot think of a good use case where you'd explicitly want `IsSubclassOf` and that would not betray your abstractions, but it's late and I cannot think well during normal hours, let alone late into the night.

When you need to list the members an interface exposes, including the members of its parents, you have to perform recursive inspection using `GetInterfaces()` and then query those results in turn for members. 

If `DataBinding` throws wrenches in your spokes because the target type is an interface, either replace it with an abstract class or use a `TypeConverter` in combination with a `TypeConverterAttribute`.





[ecma355]: http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-335.pdf
[ecma334]: http://www.ecma-international.org/publications/files/ECMA-ST/Ecma-334.pdf

