type CoreNode = { tag: "Literal"; value: number };
type PluginNode = CoreNode | { tag: "Plugin"; name: string };
export function embed(node: CoreNode): PluginNode { return node; }
export function evalCore(node: CoreNode): number { return node.value; }
export function evalPlugin(node: PluginNode): number {
  switch (node.tag) {
    case "Literal": return evalCore(node);
    case "Plugin": throw new Error("plugin semantics required");
  }
}
