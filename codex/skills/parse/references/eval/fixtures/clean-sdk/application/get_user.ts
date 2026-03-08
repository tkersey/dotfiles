import type { UserStore } from "../ports/user_store"

export async function getUser(store: UserStore, id: string) {
  return store.load(id)
}
