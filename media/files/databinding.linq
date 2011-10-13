<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\System.Windows.Forms.dll</Reference>
  <Namespace>System.ComponentModel</Namespace>
  <Namespace>System.Globalization</Namespace>
  <Namespace>System.Windows.Forms</Namespace>
</Query>

void Main()
{
  MyForm viewBase = new MyForm { Text = "Base" }, viewDerived = new MyForm { Text = "Derived" };
  var viewModel = new MyViewModel();

  viewBase.DataBindings.Add("Base", viewModel, "Base", false, DataSourceUpdateMode.OnPropertyChanged);
  viewDerived.DataBindings.Add("Derived", viewModel, "Derived", false, DataSourceUpdateMode.OnPropertyChanged);

  viewBase.Show();
  viewDerived.Show();
}

// Define other methods and classes here
interface IBase {
  string BaseMethod();
}
interface IDerived : IBase {
  string DerivedMethod();
}

class Base: IBase {
  public string BaseMethod() {return "BaseMethod"; }
}
[TypeConverter(typeof(DerivedConverter))]
class Derived : Base, IDerived {
  public string DerivedMethod(){return "DerivedMethod"; }
}

class DerivedConverter : TypeConverter {
  private readonly Type typeD = typeof(Derived);
  public override bool CanConvertTo(ITypeDescriptorContext context, Type destinationType) {
    if (destinationType.IsAssignableFrom(typeD)) return true;
    return base.CanConvertFrom(context, destinationType);
   }
   
  public override object ConvertTo(ITypeDescriptorContext context, CultureInfo culture, 
                   object value, Type destinationType) {  
    if (destinationType.IsAssignableFrom(typeD)) return value;
    return base.ConvertTo(context, culture, value, destinationType);
  }
}


class MyForm : Form {
  public IBase Base { get; set; }
  public IDerived Derived { get ; set; }
  protected override void OnLoad(EventArgs e) {
    (Base == null ? "Base is null" : Base.BaseMethod()).Dump("MyForm." + this.Text);
    (Derived == null ? "Derived is null" : Derived.DerivedMethod()).Dump("MyForm." + this.Text);
  }
}
class MyViewModel  {
  public IBase Base { get { return new Base(); } }
  public IDerived Derived { get { return new Derived(); } }
}
