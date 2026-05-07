// Rust-shaped engineering encodings of Lan/Ran ideas.
// This is not a full higher-kinded categorical implementation.

pub struct Lan<KI, DI, A> {
    pub witness: &'static str,
    pub project: Box<dyn Fn(KI) -> A>,
    pub payload: DI,
}

impl<KI, DI, A> Lan<KI, DI, A> {
    pub fn new(witness: &'static str, project: impl Fn(KI) -> A + 'static, payload: DI) -> Self {
        Self { witness, project: Box::new(project), payload }
    }
}

pub trait Ran<A> {
    type Observation<I>;
    fn run<I, Observe>(&self, observe: Observe) -> Self::Observation<I>
    where
        Observe: Fn(&A) -> I;
}

#[cfg(test)]
mod tests {
    #[derive(Clone, Debug, PartialEq)]
    enum Core { Lit(i32), Add(Box<Core>, Box<Core>) }
    #[derive(Clone, Debug, PartialEq)]
    enum Plugin { Core(Core), Mul(Box<Plugin>, Box<Plugin>) }

    fn embed(c: Core) -> Plugin { Plugin::Core(c) }

    fn eval_core(c: &Core) -> i32 {
        match c {
            Core::Lit(n) => *n,
            Core::Add(a, b) => eval_core(a) + eval_core(b),
        }
    }

    fn eval_plugin(p: &Plugin) -> i32 {
        match p {
            Plugin::Core(c) => eval_core(c),
            Plugin::Mul(a, b) => eval_plugin(a) * eval_plugin(b),
        }
    }

    #[test]
    fn lan_unit_compatibility() {
        let c = Core::Add(Box::new(Core::Lit(2)), Box::new(Core::Lit(3)));
        assert_eq!(eval_plugin(&embed(c.clone())), eval_core(&c));
    }
}
