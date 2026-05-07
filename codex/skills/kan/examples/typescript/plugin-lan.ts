type CoreNode =
  | { tag: "lit"; value: number }
  | { tag: "add"; left: CoreNode; right: CoreNode };

type PluginNode =
  | { tag: "core"; node: CoreNode }
  | { tag: "mul"; left: PluginNode; right: PluginNode };

function embed(node: CoreNode): PluginNode {
  return { tag: "core", node };
}

function evalCore(node: CoreNode): number {
  switch (node.tag) {
    case "lit": return node.value;
    case "add": return evalCore(node.left) + evalCore(node.right);
  }
}

function evalPlugin(node: PluginNode): number {
  switch (node.tag) {
    case "core": return evalCore(node.node); // eta compatibility path
    case "mul": return evalPlugin(node.left) * evalPlugin(node.right);
  }
}

const expr: CoreNode = { tag: "add", left: { tag: "lit", value: 2 }, right: { tag: "lit", value: 3 } };
if (evalPlugin(embed(expr)) !== evalCore(expr)) {
  throw new Error("Lan unit compatibility failed");
}
