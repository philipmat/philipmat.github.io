<Query Kind="Program" />

void Main()
{
  BindingFlags inst_pub = BindingFlags.Instance | BindingFlags.Public,
    flat_inst_pub = BindingFlags.FlattenHierarchy | inst_pub,
    decl_inst_pub = BindingFlags.DeclaredOnly | inst_pub;
  Action<string, Array> logm = (s, a) => a.Length.Dump(s);

  Derived d = new Derived();
  Type iB = typeof(IBase),
  iD = typeof(IDerived),
  cB = typeof(Base),
  cD = d.GetType();
  
  logm("Instance | Public", iD.GetMethods(inst_pub));                   //=> 1
  logm("Flatten | Instance | Public", iD.GetMethods(flat_inst_pub));    //=> 1
  
  
  logm("Instance | Public", cD.GetMethods(inst_pub));                   //=> 6
  logm("Flatten | Instance | Public", cD.GetMethods(flat_inst_pub));    //=> 6
  logm("Declared | Instance | Public", cD.GetMethods(decl_inst_pub));   //=> 1

  cD.IsSubclassOf(cB).Dump("Derived subclass of Base?");                //=> True
  (d is Base).Dump("Derived is Base");                                  //=> True
  cD.IsSubclassOf(iD).Dump("Derived subclass of IDerived?");            //=> False
  (d is IDerived).Dump("Derived is IDerived");                          //=> True
  
  iD.IsAssignableFrom(cD).Dump("Derived assignable to IDerived?");       //=> True
  iD.IsSubclassOf(iB).Dump("IDerived subclass of IBase?");               //=> False
  iB.IsAssignableFrom(iD).Dump("IDerived assignable IBase?");            //=> True
}

// Define other methods and classes here

interface IBase {
  void BaseMethod();
}
interface IDerived : IBase {
  void DerivedMethod();
}

class Base: IBase {
  public void BaseMethod() {}
}
class Derived : Base, IDerived {
  public void DerivedMethod(){}
}
